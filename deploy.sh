#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    # Check Docker
    if ! command_exists docker; then
        echo "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command_exists docker-compose; then
        echo "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check kubectl if deploying to Kubernetes
    if [ "$1" = "kubernetes" ]; then
        if ! command_exists kubectl; then
            echo "kubectl is not installed. Please install kubectl first."
            exit 1
        fi
        
        # Check if kubectl can connect to cluster
        if ! kubectl cluster-info >/dev/null 2>&1; then
            echo "Cannot connect to Kubernetes cluster. Please check your configuration."
            exit 1
        fi
        
        # Check if Helm is installed for monitoring
        if ! command_exists helm; then
            echo "Helm is not installed. Please install Helm for monitoring setup."
            echo "You can install it with: curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash"
            read -p "Do you want to continue without monitoring? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
}

# Function to create .env file
create_env_file() {
    echo "Creating .env file..."
    cat > .env << EOL
# Wazuh Configuration
WAZUH_MANAGER_PASSWORD=ChangeMe123!

# MCP Platform Configuration
JWT_SECRET=ChangeMe123!
OPENAI_API_KEY=your-openai-api-key
MCP_API_KEY=your-mcp-api-key

# AWS Configuration (for Terraform)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1

# Backup Configuration
BACKUP_BUCKET=your-backup-bucket
EOL
    echo "Please update the .env file with your actual values."
}

# Function to deploy using Docker Compose
deploy_docker_compose() {
    echo "Deploying using Docker Compose..."
    docker-compose up -d
    echo "Deployment complete. You can access:"
    echo "Wazuh Dashboard: https://localhost:443"
    echo "MCP Platform: http://localhost:8000"
}

# Function to deploy using Kubernetes
deploy_kubernetes() {
    echo "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl apply -f kubernetes/namespace.yaml
    
    # Create secrets
    kubectl apply -f kubernetes/secrets.yaml
    
    # Create configmaps
    kubectl apply -f kubernetes/configmaps.yaml
    
    # Deploy Wazuh
    kubectl apply -f kubernetes/wazuh.yaml
    
    # Deploy MCP Platform
    kubectl apply -f kubernetes/mcp-platform.yaml
    
    # Create network policies
    kubectl apply -f kubernetes/network-policies.yaml
    
    # Create ingress
    kubectl apply -f kubernetes/ingress.yaml
    
    # Setup monitoring if Helm is available
    if command_exists helm; then
        echo "Setting up monitoring..."
        
        # Add Prometheus Helm repo
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo update
        
        # Install Prometheus and Grafana
        helm install prometheus prometheus-community/kube-prometheus-stack \
          --namespace asoc-mcp \
          --create-namespace \
          --set grafana.enabled=true \
          --set prometheus.enabled=true
        
        # Apply monitoring configurations
        kubectl apply -f kubernetes/monitoring.yaml
    else
        echo "Skipping monitoring setup. Helm is not installed."
    fi
    
    # Setup backup
    echo "Setting up backup..."
    kubectl apply -f kubernetes/backup.yaml
    
    echo "Deployment complete. Please update your DNS records to point to your cluster's ingress IP."
    echo "You can access:"
    echo "Wazuh Dashboard: https://wazuh.yourdomain.com"
    echo "MCP Platform: https://mcp.yourdomain.com"
    echo "Grafana Dashboard: https://grafana.yourdomain.com (if monitoring is enabled)"
}

# Function to restore from backup
restore_backup() {
    if [ "$1" = "kubernetes" ]; then
        echo "Restoring from backup..."
        
        # Get backup date
        read -p "Enter backup date (YYYY-MM-DD): " backup_date
        
        # Create restore job
        cat > restore-job.yaml << EOL
apiVersion: batch/v1
kind: Job
metadata:
  name: asoc-mcp-restore
  namespace: asoc-mcp
spec:
  template:
    spec:
      containers:
      - name: restore
        image: bitnami/kubectl:latest
        command:
        - /bin/sh
        - -c
        - |
          # Download backup from S3
          aws s3 cp --recursive s3://your-backup-bucket/asoc-mcp-backups/${backup_date}/ /restore/
          
          # Restore Wazuh data
          kubectl cp /restore/wazuh-data-backup.tar.gz asoc-mcp/wazuh-manager-0:/tmp/
          kubectl exec -n asoc-mcp wazuh-manager-0 -- tar -xzf /tmp/wazuh-data-backup.tar.gz -C /var/ossec/data
          
          # Restore Wazuh logs
          kubectl cp /restore/wazuh-logs-backup.tar.gz asoc-mcp/wazuh-manager-0:/tmp/
          kubectl exec -n asoc-mcp wazuh-manager-0 -- tar -xzf /tmp/wazuh-logs-backup.tar.gz -C /var/ossec/logs
          
          # Restore MCP Platform data
          kubectl cp /restore/mcp-data-backup.tar.gz asoc-mcp/\$(kubectl get pod -n asoc-mcp -l app=mcp-platform -o jsonpath="{.items[0].metadata.name}"):/tmp/
          kubectl exec -n asoc-mcp \$(kubectl get pod -n asoc-mcp -l app=mcp-platform -o jsonpath="{.items[0].metadata.name}") -- tar -xzf /tmp/mcp-data-backup.tar.gz -C /app/data
          
          # Restore MCP Platform logs
          kubectl cp /restore/mcp-logs-backup.tar.gz asoc-mcp/\$(kubectl get pod -n asoc-mcp -l app=mcp-platform -o jsonpath="{.items[0].metadata.name}"):/tmp/
          kubectl exec -n asoc-mcp \$(kubectl get pod -n asoc-mcp -l app=mcp-platform -o jsonpath="{.items[0].metadata.name}") -- tar -xzf /tmp/mcp-logs-backup.tar.gz -C /app/logs
          
          # Restart services
          kubectl rollout restart statefulset wazuh-manager -n asoc-mcp
          kubectl rollout restart deployment mcp-platform -n asoc-mcp
        volumeMounts:
        - name: restore-volume
          mountPath: /restore
        - name: aws-credentials
          mountPath: /root/.aws
          readOnly: true
      volumes:
      - name: restore-volume
        emptyDir: {}
      - name: aws-credentials
        secret:
          secretName: aws-credentials
      restartPolicy: OnFailure
EOL
        
        # Apply restore job
        kubectl apply -f restore-job.yaml
        
        echo "Restore job created. You can check the status with: kubectl get jobs -n asoc-mcp"
    else
        echo "Restore is only supported for Kubernetes deployments."
    fi
}

# Main script
case "$1" in
    "docker-compose")
        check_prerequisites "docker-compose"
        create_env_file
        deploy_docker_compose
        ;;
    "kubernetes")
        check_prerequisites "kubernetes"
        create_env_file
        deploy_kubernetes
        ;;
    "restore")
        if [ -z "$2" ]; then
            echo "Usage: $0 restore {docker-compose|kubernetes}"
            exit 1
        fi
        restore_backup "$2"
        ;;
    *)
        echo "Usage: $0 {docker-compose|kubernetes|restore}"
        exit 1
        ;;
esac 