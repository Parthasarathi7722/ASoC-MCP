from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
import os
import redis
import json
import logging
import asyncio
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
import httpx
import elasticsearch
from elasticsearch import AsyncElasticsearch
import pymongo
from pymongo import MongoClient
import psycopg2
import mysql.connector
import splunklib.client as splunk
import tenable.io
import rapid7.vm
from abc import ABC, abstractmethod

app = FastAPI(title="Data Source Connectors Service")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv("MEMORY_URL", "redis://memory:6379").split("://")[1].split(":")[0],
    port=6379,
    decode_responses=True
)

# OAuth2 scheme for JWT validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://auth-service:8000/token")

# Models
class DataSourceConfig(BaseModel):
    name: str
    type: str
    enabled: bool = True
    config: Dict[str, Any]
    description: Optional[str] = None
    tags: List[str] = []

class DataSourceStatus(BaseModel):
    source_id: str
    name: str
    type: str
    status: str
    last_sync: Optional[str] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = {}

class DataQuery(BaseModel):
    source_id: str
    query_type: str
    parameters: Dict[str, Any]
    limit: int = 100
    timeout: int = 30

class DataQueryResult(BaseModel):
    query_id: str
    source_id: str
    status: str
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: str

# Abstract base class for data source connectors
class DataSourceConnector(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.connected = False
        self.last_sync = None
        self.error = None
        self.metrics = {}

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the data source."""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the data source."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the connection to the data source."""
        pass

    @abstractmethod
    async def query(self, query_type: str, parameters: Dict[str, Any], limit: int = 100, timeout: int = 30) -> List[Dict[str, Any]]:
        """Execute a query on the data source."""
        pass

    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get metrics about the data source."""
        pass

# Elasticsearch Connector
class ElasticsearchConnector(DataSourceConnector):
    async def connect(self) -> bool:
        try:
            self.client = AsyncElasticsearch(
                hosts=[self.config["host"]],
                basic_auth=(self.config["username"], self.config["password"]),
                verify_certs=self.config.get("verify_certs", True),
                timeout=self.config.get("timeout", 30)
            )
            self.connected = await self.client.ping()
            return self.connected
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to connect to Elasticsearch: {self.error}")
            return False

    async def disconnect(self) -> bool:
        try:
            if self.client:
                await self.client.close()
            self.connected = False
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to disconnect from Elasticsearch: {self.error}")
            return False

    async def test_connection(self) -> bool:
        try:
            return await self.client.ping()
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to test Elasticsearch connection: {self.error}")
            return False

    async def query(self, query_type: str, parameters: Dict[str, Any], limit: int = 100, timeout: int = 30) -> List[Dict[str, Any]]:
        try:
            if query_type == "search":
                response = await self.client.search(
                    index=parameters["index"],
                    body=parameters["query"],
                    size=limit,
                    timeout=f"{timeout}s"
                )
                return [hit["_source"] for hit in response["hits"]["hits"]]
            elif query_type == "get":
                response = await self.client.get(
                    index=parameters["index"],
                    id=parameters["id"]
                )
                return [response["_source"]]
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to execute Elasticsearch query: {self.error}")
            return []

    async def get_metrics(self) -> Dict[str, Any]:
        try:
            stats = await self.client.cluster.stats()
            return {
                "cluster_name": stats["cluster_name"],
                "node_count": stats["nodes"]["count"]["total"],
                "document_count": stats["indices"]["docs"]["count"],
                "storage_size": stats["indices"]["store"]["size_in_bytes"]
            }
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to get Elasticsearch metrics: {self.error}")
            return {}

# MongoDB Connector
class MongoDBConnector(DataSourceConnector):
    async def connect(self) -> bool:
        try:
            self.client = MongoClient(
                host=self.config["host"],
                port=self.config.get("port", 27017),
                username=self.config.get("username"),
                password=self.config.get("password"),
                authSource=self.config.get("auth_source", "admin"),
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command('ping')
            self.connected = True
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to connect to MongoDB: {self.error}")
            return False

    async def disconnect(self) -> bool:
        try:
            if self.client:
                self.client.close()
            self.connected = False
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to disconnect from MongoDB: {self.error}")
            return False

    async def test_connection(self) -> bool:
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to test MongoDB connection: {self.error}")
            return False

    async def query(self, query_type: str, parameters: Dict[str, Any], limit: int = 100, timeout: int = 30) -> List[Dict[str, Any]]:
        try:
            db = self.client[parameters["database"]]
            collection = db[parameters["collection"]]
            
            if query_type == "find":
                cursor = collection.find(
                    parameters.get("filter", {}),
                    parameters.get("projection", None)
                ).limit(limit)
                
                return list(cursor)
            elif query_type == "aggregate":
                cursor = collection.aggregate(
                    parameters["pipeline"],
                    allowDiskUse=True
                ).limit(limit)
                
                return list(cursor)
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to execute MongoDB query: {self.error}")
            return []

    async def get_metrics(self) -> Dict[str, Any]:
        try:
            stats = self.client.admin.command("serverStatus")
            return {
                "connections": stats["connections"],
                "opcounters": stats["opcounters"],
                "mem": stats["mem"]
            }
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to get MongoDB metrics: {self.error}")
            return {}

# PostgreSQL Connector
class PostgreSQLConnector(DataSourceConnector):
    async def connect(self) -> bool:
        try:
            self.client = psycopg2.connect(
                host=self.config["host"],
                port=self.config.get("port", 5432),
                database=self.config["database"],
                user=self.config["username"],
                password=self.config["password"]
            )
            self.connected = True
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to connect to PostgreSQL: {self.error}")
            return False

    async def disconnect(self) -> bool:
        try:
            if self.client:
                self.client.close()
            self.connected = False
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to disconnect from PostgreSQL: {self.error}")
            return False

    async def test_connection(self) -> bool:
        try:
            with self.client.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to test PostgreSQL connection: {self.error}")
            return False

    async def query(self, query_type: str, parameters: Dict[str, Any], limit: int = 100, timeout: int = 30) -> List[Dict[str, Any]]:
        try:
            with self.client.cursor() as cursor:
                if query_type == "select":
                    cursor.execute(
                        parameters["query"],
                        parameters.get("params", ())
                    )
                    columns = [desc[0] for desc in cursor.description]
                    results = []
                    for row in cursor.fetchmany(limit):
                        results.append(dict(zip(columns, row)))
                    return results
                else:
                    raise ValueError(f"Unsupported query type: {query_type}")
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to execute PostgreSQL query: {self.error}")
            return []

    async def get_metrics(self) -> Dict[str, Any]:
        try:
            with self.client.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        numbackends as active_connections,
                        xact_commit as transactions_committed,
                        xact_rollback as transactions_rolled_back,
                        blks_read as blocks_read,
                        blks_hit as blocks_hit,
                        tup_returned as rows_returned,
                        tup_fetched as rows_fetched,
                        tup_inserted as rows_inserted,
                        tup_updated as rows_updated,
                        tup_deleted as rows_deleted
                    FROM pg_stat_database
                    WHERE datname = current_database()
                """)
                columns = [desc[0] for desc in cursor.description]
                row = cursor.fetchone()
                return dict(zip(columns, row))
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to get PostgreSQL metrics: {self.error}")
            return {}

# MySQL Connector
class MySQLConnector(DataSourceConnector):
    async def connect(self) -> bool:
        try:
            self.client = mysql.connector.connect(
                host=self.config["host"],
                port=self.config.get("port", 3306),
                database=self.config["database"],
                user=self.config["username"],
                password=self.config["password"]
            )
            self.connected = True
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to connect to MySQL: {self.error}")
            return False

    async def disconnect(self) -> bool:
        try:
            if self.client:
                self.client.close()
            self.connected = False
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to disconnect from MySQL: {self.error}")
            return False

    async def test_connection(self) -> bool:
        try:
            with self.client.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to test MySQL connection: {self.error}")
            return False

    async def query(self, query_type: str, parameters: Dict[str, Any], limit: int = 100, timeout: int = 30) -> List[Dict[str, Any]]:
        try:
            with self.client.cursor(dictionary=True) as cursor:
                if query_type == "select":
                    cursor.execute(
                        parameters["query"],
                        parameters.get("params", ())
                    )
                    return cursor.fetchmany(limit)
                else:
                    raise ValueError(f"Unsupported query type: {query_type}")
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to execute MySQL query: {self.error}")
            return []

    async def get_metrics(self) -> Dict[str, Any]:
        try:
            with self.client.cursor(dictionary=True) as cursor:
                cursor.execute("SHOW GLOBAL STATUS")
                status = cursor.fetchall()
                return {row["Variable_name"]: row["Value"] for row in status}
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to get MySQL metrics: {self.error}")
            return {}

# Splunk Connector
class SplunkConnector(DataSourceConnector):
    async def connect(self) -> bool:
        try:
            self.client = splunk.connect(
                host=self.config["host"],
                port=self.config.get("port", 8089),
                username=self.config["username"],
                password=self.config["password"],
                scheme=self.config.get("scheme", "https")
            )
            self.connected = True
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to connect to Splunk: {self.error}")
            return False

    async def disconnect(self) -> bool:
        try:
            if self.client:
                self.client.logout()
            self.connected = False
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to disconnect from Splunk: {self.error}")
            return False

    async def test_connection(self) -> bool:
        try:
            self.client.info()
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to test Splunk connection: {self.error}")
            return False

    async def query(self, query_type: str, parameters: Dict[str, Any], limit: int = 100, timeout: int = 30) -> List[Dict[str, Any]]:
        try:
            if query_type == "search":
                search_query = parameters["query"]
                job = self.client.jobs.create(search_query, **parameters.get("options", {}))
                
                # Wait for the job to complete
                while not job.is_done():
                    time.sleep(1)
                
                # Get the results
                result_count = job["resultCount"]
                if result_count > limit:
                    result_count = limit
                
                results = []
                for i in range(result_count):
                    result = job.results[i]
                    results.append(result)
                
                return results
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to execute Splunk query: {self.error}")
            return []

    async def get_metrics(self) -> Dict[str, Any]:
        try:
            return {
                "server_info": self.client.info(),
                "system_health": self.client.system_health()
            }
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to get Splunk metrics: {self.error}")
            return {}

# Tenable.io Connector
class TenableConnector(DataSourceConnector):
    async def connect(self) -> bool:
        try:
            self.client = tenable.io.TenableIO(
                access_key=self.config["access_key"],
                secret_key=self.config["secret_key"]
            )
            self.connected = True
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to connect to Tenable.io: {self.error}")
            return False

    async def disconnect(self) -> bool:
        try:
            if self.client:
                self.client.logout()
            self.connected = False
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to disconnect from Tenable.io: {self.error}")
            return False

    async def test_connection(self) -> bool:
        try:
            self.client.server.status()
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to test Tenable.io connection: {self.error}")
            return False

    async def query(self, query_type: str, parameters: Dict[str, Any], limit: int = 100, timeout: int = 30) -> List[Dict[str, Any]]:
        try:
            if query_type == "vulnerabilities":
                vulns = self.client.vulns.list(
                    limit=limit,
                    **parameters.get("filters", {})
                )
                return list(vulns)
            elif query_type == "scans":
                scans = self.client.scans.list(
                    limit=limit,
                    **parameters.get("filters", {})
                )
                return list(scans)
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to execute Tenable.io query: {self.error}")
            return []

    async def get_metrics(self) -> Dict[str, Any]:
        try:
            return {
                "server_status": self.client.server.status(),
                "vulnerability_count": self.client.vulns.count(),
                "scan_count": self.client.scans.count()
            }
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to get Tenable.io metrics: {self.error}")
            return {}

# Rapid7 InsightVM Connector
class Rapid7Connector(DataSourceConnector):
    async def connect(self) -> bool:
        try:
            self.client = rapid7.vm.Console(
                hostname=self.config["host"],
                port=self.config.get("port", 3780),
                username=self.config["username"],
                password=self.config["password"],
                ssl_verify=self.config.get("ssl_verify", True)
            )
            self.connected = True
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to connect to Rapid7 InsightVM: {self.error}")
            return False

    async def disconnect(self) -> bool:
        try:
            if self.client:
                self.client.logout()
            self.connected = False
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to disconnect from Rapid7 InsightVM: {self.error}")
            return False

    async def test_connection(self) -> bool:
        try:
            self.client.system_info()
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to test Rapid7 InsightVM connection: {self.error}")
            return False

    async def query(self, query_type: str, parameters: Dict[str, Any], limit: int = 100, timeout: int = 30) -> List[Dict[str, Any]]:
        try:
            if query_type == "vulnerabilities":
                vulns = self.client.get_vulnerabilities(
                    limit=limit,
                    **parameters.get("filters", {})
                )
                return list(vulns)
            elif query_type == "assets":
                assets = self.client.get_assets(
                    limit=limit,
                    **parameters.get("filters", {})
                )
                return list(assets)
            elif query_type == "scans":
                scans = self.client.get_scans(
                    limit=limit,
                    **parameters.get("filters", {})
                )
                return list(scans)
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to execute Rapid7 InsightVM query: {self.error}")
            return []

    async def get_metrics(self) -> Dict[str, Any]:
        try:
            return {
                "system_info": self.client.system_info(),
                "vulnerability_count": self.client.get_vulnerability_count(),
                "asset_count": self.client.get_asset_count(),
                "scan_count": self.client.get_scan_count()
            }
        except Exception as e:
            self.error = str(e)
            logger.error(f"Failed to get Rapid7 InsightVM metrics: {self.error}")
            return {}

# Connector factory
def get_connector(source_type: str, config: Dict[str, Any]) -> DataSourceConnector:
    connectors = {
        "elasticsearch": ElasticsearchConnector,
        "mongodb": MongoDBConnector,
        "postgresql": PostgreSQLConnector,
        "mysql": MySQLConnector,
        "splunk": SplunkConnector,
        "tenable": TenableConnector,
        "rapid7": Rapid7Connector
    }
    
    if source_type not in connectors:
        raise ValueError(f"Unsupported data source type: {source_type}")
    
    return connectors[source_type](config)

# Store active connectors
active_connectors = {}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # In a real implementation, validate JWT token
        return "user"  # Simplified for demo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@app.post("/sources", response_model=DataSourceStatus)
async def create_data_source(
    source: DataSourceConfig,
    current_user: str = Depends(get_current_user)
):
    """
    Create a new data source connector.
    """
    try:
        # Generate a unique source ID
        import uuid
        source_id = str(uuid.uuid4())
        
        # Create the connector
        connector = get_connector(source.type, source.config)
        
        # Test the connection
        connected = await connector.connect()
        
        # Store the connector
        active_connectors[source_id] = {
            "connector": connector,
            "config": source.dict()
        }
        
        # Store the configuration in Redis
        redis_client.set(
            f"datasource:{source_id}",
            json.dumps(source.dict()),
            ex=86400 * 30  # Expire after 30 days
        )
        
        # Get metrics
        metrics = await connector.get_metrics()
        
        return DataSourceStatus(
            source_id=source_id,
            name=source.name,
            type=source.type,
            status="connected" if connected else "error",
            last_sync=datetime.now().isoformat(),
            error=connector.error,
            metrics=metrics
        )
        
    except Exception as e:
        logger.error(f"Error creating data source: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/sources", response_model=List[DataSourceStatus])
async def list_data_sources(current_user: str = Depends(get_current_user)):
    """
    List all data source connectors.
    """
    try:
        sources = []
        
        for source_id, source_data in active_connectors.items():
            connector = source_data["connector"]
            config = source_data["config"]
            
            # Test the connection
            connected = await connector.test_connection()
            
            # Get metrics
            metrics = await connector.get_metrics()
            
            sources.append(DataSourceStatus(
                source_id=source_id,
                name=config["name"],
                type=config["type"],
                status="connected" if connected else "error",
                last_sync=connector.last_sync,
                error=connector.error,
                metrics=metrics
            ))
        
        return sources
        
    except Exception as e:
        logger.error(f"Error listing data sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/sources/{source_id}", response_model=DataSourceStatus)
async def get_data_source(
    source_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get a specific data source connector.
    """
    try:
        if source_id not in active_connectors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        source_data = active_connectors[source_id]
        connector = source_data["connector"]
        config = source_data["config"]
        
        # Test the connection
        connected = await connector.test_connection()
        
        # Get metrics
        metrics = await connector.get_metrics()
        
        return DataSourceStatus(
            source_id=source_id,
            name=config["name"],
            type=config["type"],
            status="connected" if connected else "error",
            last_sync=connector.last_sync,
            error=connector.error,
            metrics=metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data source: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/sources/{source_id}")
async def delete_data_source(
    source_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Delete a data source connector.
    """
    try:
        if source_id not in active_connectors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        source_data = active_connectors[source_id]
        connector = source_data["connector"]
        
        # Disconnect from the data source
        await connector.disconnect()
        
        # Remove the connector
        del active_connectors[source_id]
        
        # Remove the configuration from Redis
        redis_client.delete(f"datasource:{source_id}")
        
        return {"message": "Data source deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting data source: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/sources/{source_id}/query", response_model=DataQueryResult)
async def query_data_source(
    source_id: str,
    query: DataQuery,
    current_user: str = Depends(get_current_user)
):
    """
    Execute a query on a data source.
    """
    try:
        if source_id not in active_connectors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found"
            )
        
        source_data = active_connectors[source_id]
        connector = source_data["connector"]
        
        # Generate a unique query ID
        import uuid
        query_id = str(uuid.uuid4())
        
        # Execute the query
        results = await connector.query(
            query.query_type,
            query.parameters,
            query.limit,
            query.timeout
        )
        
        # Store the query result in Redis
        query_result = {
            "query_id": query_id,
            "source_id": source_id,
            "status": "completed",
            "results": results,
            "metadata": {
                "query_type": query.query_type,
                "parameters": query.parameters,
                "limit": query.limit,
                "timeout": query.timeout
            },
            "timestamp": datetime.now().isoformat()
        }
        
        redis_client.set(
            f"query:{query_id}",
            json.dumps(query_result),
            ex=3600  # Expire after 1 hour
        )
        
        return DataQueryResult(**query_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/queries/{query_id}", response_model=DataQueryResult)
async def get_query_result(
    query_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    Get the result of a query.
    """
    try:
        query_data = redis_client.get(f"query:{query_id}")
        
        if not query_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query result not found"
            )
        
        return DataQueryResult(**json.loads(query_data))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting query result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 