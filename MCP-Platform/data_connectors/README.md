# Data Source Connectors Service

This service provides a unified interface for connecting to and querying various security data sources. It supports multiple data source types and provides a consistent API for data access.

## Supported Data Sources

- Elasticsearch
- MongoDB
- PostgreSQL
- MySQL
- Splunk
- Tenable.io
- Rapid7 InsightVM

## Features

- Unified API for all data sources
- Connection management and pooling
- Query execution and result formatting
- Health checks and metrics
- Authentication and authorization
- Error handling and logging

## Configuration

1. Copy `config/sample_config.json` to `config/config.json`
2. Update the configuration with your data source credentials
3. Set environment variables:
   - `REDIS_HOST`: Redis host (default: localhost)
   - `REDIS_PORT`: Redis port (default: 6379)
   - `JWT_SECRET`: Secret key for JWT tokens
   - `JWT_ALGORITHM`: JWT algorithm (default: HS256)

## API Endpoints

### Data Sources

- `POST /datasources`: Create a new data source
- `GET /datasources`: List all data sources
- `GET /datasources/{source_id}`: Get data source details
- `DELETE /datasources/{source_id}`: Delete a data source
- `POST /datasources/{source_id}/test`: Test data source connection
- `GET /datasources/{source_id}/metrics`: Get data source metrics

### Queries

- `POST /datasources/{source_id}/query`: Execute a query
- `GET /queries/{query_id}`: Get query results
- `GET /queries/{query_id}/status`: Get query status

### Health

- `GET /health`: Service health check

## Docker Deployment

1. Build the image:
   ```bash
   docker build -t mcp-data-connectors .
   ```

2. Run the container:
   ```bash
   docker run -d \
     -p 8000:8000 \
     -v $(pwd)/config:/app/config \
     -e REDIS_HOST=redis \
     -e REDIS_PORT=6379 \
     -e JWT_SECRET=your_secret \
     mcp-data-connectors
   ```

## Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:
   ```bash
   uvicorn app:app --reload
   ```

3. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

## Testing

Run the test suite:
```bash
pytest
```

## Security Considerations

- All credentials are stored securely in Redis
- JWT tokens are required for authentication
- SSL/TLS is supported for all data sources
- Rate limiting is implemented for API endpoints
- Input validation is performed on all requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 