# CloudShop Microservices

CloudShop is a cloud-native e-commerce microservices project built to practice and demonstrate real-world Cloud and DevOps concepts.

The project is being developed incrementally, starting with local microservice development, Docker containerization, multi-container orchestration, Redis caching, and PostgreSQL-based persistent storage. It will later be extended with reverse proxy routing, CI/CD, Kubernetes, cloud deployment, Infrastructure as Code, and observability.

## Project Goals

The main goals of this project are to:

- Build an e-commerce backend using a microservices architecture
- Develop independent backend services
- Containerize services with Docker
- Practice Docker networking and service discovery
- Manage multi-container environments with Docker Compose
- Implement service-to-service communication
- Implement caching with Redis
- Implement persistent data storage with PostgreSQL
- Work with a large real-world e-commerce dataset
- Practice database indexing, filtering, search, and pagination
- Manage application configuration using environment variables
- Practice service health checks and failure handling
- Apply CI/CD practices with GitHub Actions
- Deploy containerized workloads to cloud environments
- Learn Infrastructure as Code with Terraform
- Learn Kubernetes deployment and service management
- Implement monitoring and observability

## Planned Architecture

CloudShop is designed to evolve into a complete cloud-native microservices platform.

The target architecture is:

```text
                         Developer
                             |
                             | git push
                             v
                          GitHub
                             |
                             v
                      GitHub Actions
                   CI / Test / Build / Scan
                             |
                             v
                     Container Registry
                             |
                             v
                            AWS
                             |
                             v
                     Kubernetes Cluster
                             |
               +-------------+-------------+
               |                           |
               v                           v
         Nginx / Ingress              Monitoring
               |                  Prometheus + Grafana
               |
       +-------+-------+-------------------+
       |               |                   |
       v               v                   v
  User Service    Product Service    Order Service
     Flask             Flask             Flask
       |                 |                 |
       v                 v                 v
    User DB          PostgreSQL         Order DB
                        |
                        v
                      Redis
                      Cache
```

### Architecture Layers

The project will gradually cover the following layers:

- **Application:** Python and Flask microservices
- **Containerization:** Docker
- **Local orchestration:** Docker Compose
- **Service discovery:** Docker Compose DNS
- **Reverse proxy / routing:** Nginx
- **Caching:** Redis
- **Persistence:** PostgreSQL, independent databases, and Docker volumes
- **Database optimization:** Pagination, filtering, and indexing
- **Version control:** Git and GitHub
- **CI/CD:** GitHub Actions
- **Infrastructure as Code:** Terraform
- **Container registry:** Container image storage and versioning
- **Cloud infrastructure:** AWS
- **Container orchestration:** Kubernetes
- **Observability:** Prometheus and Grafana
- **Security:** Secrets management, non-root containers, dependency and image vulnerability scanning

Each stage is implemented incrementally rather than added only as documentation.

## Current Project Structure

```text
cloudshop-microservices/
│
├── compose.yaml
├── .env.example
│
├── scripts/
│   └── import_products.py
│
├── services/
│   │
│   ├── user-service/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   │
│   ├── product-service/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   │
│   └── order-service/
│       ├── app.py
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .dockerignore
│
├── nginx/
│
└── README.md
```

## Microservices

CloudShop currently contains three independent Flask microservices.

### User Service

The User Service was the first microservice implemented in the project.

It currently provides a health check endpoint:

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

The service runs on port:

```text
5000
```

The health endpoint can later be used by container orchestration platforms, load balancers, and monitoring systems to verify service availability.

### Product Service

The Product Service manages the product API and uses PostgreSQL as its persistent source of truth.

Available endpoints:

```http
GET /health
GET /products
GET /products/<article_id>
```

`GET /products` supports pagination, product-name search, and color filtering.

Examples:

```http
GET /products?page=1&limit=20
GET /products?page=1&limit=5&search=shirt
GET /products?page=1&limit=5&color=Black
GET /products?page=1&limit=5&search=shirt&color=Black
```

Product Service uses Redis as a caching layer in front of PostgreSQL.

When the endpoint is requested, Product Service first checks Redis for the requested query.

If cached data exists:

```text
Cache HIT → Redis → Response
```

If cached data does not exist:

```text
Cache MISS → PostgreSQL → Redis Cache → Response
```

Cache keys include pagination and filtering parameters so different queries are cached independently.

Example:

```text
products:page:1:limit:20:search:shirt:color:Black
```

`GET /products/<article_id>` retrieves a specific product directly from PostgreSQL.

If the requested product does not exist, the API returns:

```text
404 Not Found
```

The service runs on port:

```text
5001
```

### Order Service

The Order Service provides the current order API.

Available endpoints:

```http
GET /health
GET /orders
GET /orders/<order_id>
```

`GET /orders` returns the available orders.

`GET /orders/<order_id>` returns a specific order based on its ID.

If the requested order does not exist, the API returns:

```text
404 Not Found
```

The service runs on port:

```text
5002
```

Order data is currently stored in memory and will later be moved to persistent storage.

## PostgreSQL Product Storage

PostgreSQL is used as the persistent source of truth for Product Service.

A large real-world e-commerce product dataset was imported into the database using a dedicated Python import script.

The current database contains:

```text
105,542 products
```

Product records include:

- Article ID
- Product code
- Product name
- Product type
- Product group
- Color
- Department
- Section
- Garment group
- Description

The dataset itself is not stored directly in the Git repository.

The import process is handled through:

```text
scripts/import_products.py
```

The import script reads the external CSV dataset and inserts product records into PostgreSQL.

Duplicate product IDs are safely handled using:

```sql
ON CONFLICT (article_id) DO NOTHING
```

This allows the import process to be rerun without failing on existing primary keys.

## Product Pagination

Because Product Service contains more than 100,000 products, the API does not return the entire dataset in a single request.

Pagination is implemented using PostgreSQL:

```sql
LIMIT
OFFSET
```

Example:

```http
GET /products?page=1&limit=20
```

The API also limits the maximum page size to prevent excessively large responses.

## Product Search and Filtering

Product Service supports product-name search and color filtering.

Product-name search uses PostgreSQL `ILIKE`:

```sql
name ILIKE '%shirt%'
```

This provides case-insensitive product-name searching.

Color filtering is also supported:

```http
GET /products?color=Black
```

Search and filtering can be combined with pagination.

## PostgreSQL Indexing

A PostgreSQL index was created for the product color column:

```sql
CREATE INDEX idx_products_color ON products(color);
```

The query execution plan was inspected using:

```sql
EXPLAIN
SELECT *
FROM products
WHERE color = 'Black';
```

PostgreSQL confirmed use of the index through:

```text
Bitmap Index Scan on idx_products_color
```

This demonstrates how indexes can improve database query performance for frequently filtered columns.

## PostgreSQL Persistent Storage

PostgreSQL data is stored using a Docker named volume:

```text
postgres_data
```

The volume is mounted to:

```text
/var/lib/postgresql/data
```

This allows database data to survive container recreation and restarts.

Persistence was verified by restarting the local environment and confirming that previously inserted product records remained available.

```text
PostgreSQL Container
        |
        v
postgres_data
 Docker Volume
        |
        v
Persistent Product Data
```

## Independent Service Environments

Each microservice is developed independently.

During local development, every service uses its own Python virtual environment.

Example:

```text
user-service/.venv
product-service/.venv
order-service/.venv
```

This keeps Python dependencies isolated between services.

A virtual environment can be created using:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Dependencies can then be installed using:

```bash
pip install -r requirements.txt
```

The local `.venv` directories are excluded from Docker build contexts and Git version control.

## Docker

All current CloudShop microservices are independently containerized with Docker.

Each service contains its own:

- Flask application
- `requirements.txt`
- `Dockerfile`
- `.dockerignore`

The Dockerfiles currently use:

```dockerfile
FROM python:3.13-slim
```

as the base image.

Each image:

1. Defines `/app` as the working directory
2. Copies `requirements.txt`
3. Installs Python dependencies
4. Copies the Flask application
5. Exposes the application's internal port
6. Starts the Flask application when the container starts

### Service Ports

| Service | Container Port | Host Port |
|---|---:|---:|
| User Service | `5000` | `5000` |
| Product Service | `5001` | `5001` |
| Order Service | `5002` | `5002` |
| Redis | `6379` | Not published |
| PostgreSQL | `5432` | `5432` |

Redis is only required by services inside the Docker Compose network, so its port is not published to the host machine.

PostgreSQL is currently published to the host during local development so the dataset import script can connect through `localhost:5432`.

## Docker Ignore

Each service uses a `.dockerignore` file to prevent unnecessary local files from being included in the Docker build context.

Current configuration:

```text
.venv
__pycache__
*.pyc
.git
.gitignore
```

This prevents local virtual environments, Python cache files, and Git-related files from being sent to the Docker build context.

## Docker Compose

Docker Compose is used to manage the CloudShop multi-container environment.

The root-level:

```text
compose.yaml
```

currently manages:

- User Service
- Product Service
- Order Service
- Redis
- PostgreSQL

The complete environment can be built and started using:

```bash
docker compose up -d --build
```

Running services can be inspected using:

```bash
docker compose ps
```

Instead of manually building and starting every container, Docker Compose manages the services, Redis, and PostgreSQL as a single application environment.

## Docker Compose Networking

Docker Compose automatically creates a shared network for the CloudShop services.

Current container architecture:

```text
                      Docker Compose Network
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
       User Service    Product Service    Order Service
           :5000            :5001            :5002
                             |
                    +--------+--------+
                    |                 |
                    v                 v
                  Redis           PostgreSQL
                  :6379             :5432
```

All containers can communicate through this internal network.

This means services do not need to know each other's dynamically assigned container IP addresses.

## DNS-Based Service Discovery

Docker Compose provides built-in DNS-based service discovery.

Containers can locate other services using their Compose service names.

For example:

```text
product-service
redis
postgres
```

Product Service connects internally to Redis using:

```text
redis:6379
```

and PostgreSQL using:

```text
postgres:5432
```

instead of relying on hard-coded container IP addresses.

For host-based development scripts, PostgreSQL can currently be accessed using:

```text
localhost:5432
```

## Container-to-Container Communication

Internal HTTP communication between containers has also been verified.

From inside the Order Service container, Product Service can be reached using:

```text
http://product-service:5001/products
```

The communication path is:

```text
Order Service
     |
     | HTTP request
     v
product-service:5001
     |
     v
Product Service
     |
     v
GET /products
```

This confirms that the services can communicate over the Docker Compose network.

Order Service does not yet automatically call Product Service from its application code. The current implementation verifies the networking and HTTP communication foundation required for future service-to-service integration.

Product Service also communicates with Redis and PostgreSQL through the Docker Compose network.

```text
Product Service
      |
      +----------> redis:6379
      |
      +----------> postgres:5432
```

## Redis Caching

Redis is integrated into the local CloudShop environment as a caching layer for Product Service.

The current cache-aside flow is:

```text
Client
  |
  v
Product Service
  |
  v
Check Redis
  |
  +---- Cache HIT ----> Return cached product data
  |
  +---- Cache MISS ---> Query PostgreSQL
                         |
                         v
                    Store in Redis
                         |
                         v
                      Response
```

Cached query results are stored with a TTL (Time To Live).

After the TTL expires, Redis automatically removes the cached entry and the next request becomes a cache miss.

The TTL is configurable using an environment variable.

Cache hit and cache miss behavior has been tested through the Product Service API.

## Redis Failure Handling

Redis is treated as an optional caching dependency rather than the primary source of product data.

Redis operations in Product Service are protected with error handling.

If Redis becomes unavailable, Product Service logs the Redis error and falls back to PostgreSQL instead of failing the entire request.

The intended behavior is:

```text
Redis available
      |
      v
Use cache normally

Redis unavailable
      |
      v
Log Redis error
      |
      v
Query PostgreSQL
      |
      v
Return HTTP 200 response
```

Redis failure was tested by stopping the Redis service while Product Service remained running.

The Product Service continued returning product data, demonstrating graceful degradation of the caching dependency.

The failure test also demonstrated that dependency failures can increase request latency even when the application remains available.

## Environment Configuration

Redis and PostgreSQL connection settings are externalized using environment variables instead of being hard-coded into Product Service.

Current configuration includes:

```text
REDIS_HOST
REDIS_PORT
CACHE_TTL

POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Docker Compose reads the local `.env` configuration and injects the required values into the containers.

The configuration flow is:

```text
.env
  |
  v
Docker Compose
  |
  v
Container Environment Variables
  |
  v
Product Service
```

The local `.env` file is excluded from Git version control.

A safe `.env.example` file is included in the repository to document required configuration without exposing environment-specific or sensitive values.

Environment variables are used for configuration externalization and are not treated as a complete secrets-management solution. Dedicated secrets management will be introduced later.

## Redis Health Check and Service Dependency

Redis includes a Docker health check using:

```text
redis-cli ping
```

A successful Redis health check returns:

```text
PONG
```

and Docker marks the Redis container as healthy.

Product Service uses Docker Compose dependency configuration with:

```yaml
depends_on:
  redis:
    condition: service_healthy
```

This ensures that Product Service waits for Redis to pass its health check during startup.

Startup dependency management does not replace runtime failure handling. If Redis becomes unavailable after startup, Product Service still relies on its application-level fallback behavior.

## Host Access vs Internal Communication

For local development, the Flask services can currently be accessed from the host machine using:

```text
http://localhost:5000
http://localhost:5001
http://localhost:5002
```

Host access:

```text
localhost:5000 → User Service
localhost:5001 → Product Service
localhost:5002 → Order Service
localhost:5432 → PostgreSQL
```

Inside the Docker Compose network, containers communicate using service names:

```text
user-service:5000
product-service:5001
order-service:5002
redis:6379
postgres:5432
```

Therefore, internal container communication does not depend on host ports or hard-coded container IP addresses.

## Current Local Architecture

```text
                           Host Machine
                               |
               +---------------+---------------+
               |               |               |
             :5000           :5001           :5002
               |               |               |
               v               v               v
         User Service    Product Service    Order Service
                              |
                       +------+------+
                       |             |
                       v             v
                     Redis       PostgreSQL
                     Cache       105K+ Products
                                     |
                                     v
                               postgres_data
                               Docker Volume
```

The current architecture establishes the multi-service foundation of CloudShop with PostgreSQL persistent storage and Redis caching for Product Service.

## Docker Operations Practiced

The following Docker operations have been practiced throughout the project:

```bash
docker build
docker images
docker run
docker ps
docker ps -a
docker logs
docker stop
docker start
docker rm
docker compose config
docker compose up
docker compose ps
docker compose exec
```

The project has also been used to practice:

- Docker images and containers
- Image tags
- Dockerfile instructions
- Build contexts
- Image layers
- Docker build cache
- Port publishing
- Container lifecycle management
- Container logs
- Multi-container applications
- Docker networking
- DNS-based service discovery
- Container-to-container HTTP communication
- Redis caching
- Cache hit and cache miss behavior
- Cache TTL
- Environment-based container configuration
- Docker health checks
- Service startup dependencies
- Runtime dependency failure handling
- PostgreSQL integration
- Docker volume persistence
- Dataset importing
- Pagination
- Product search and filtering
- PostgreSQL indexing
- SQL query-plan inspection with `EXPLAIN`

## Development Workflow

The project follows a local development and Git-based workflow:

```text
Local Development
       |
       v
VS Code
       |
       v
Git
       |
       v
GitHub
       |
       v
CI/CD (planned)
       |
       v
Container Registry (planned)
       |
       v
AWS / Kubernetes (planned)
```

AWS infrastructure is intended to be used as a deployment environment rather than as the primary development workstation.

## Current Progress

Completed:

- Initial microservices architecture defined
- Repository structure created
- Independent Python development environments configured
- User Service created and containerized
- Product Service created and containerized
- Order Service created and containerized
- Health endpoints implemented and tested
- Product API endpoints implemented and tested
- Order API endpoints implemented and tested
- `404 Not Found` API behavior tested
- Python dependencies documented with `requirements.txt`
- `.dockerignore` configured for services
- Dockerfiles created
- Docker images successfully built
- Containers successfully tested independently
- Port mappings tested
- Container logs inspected
- Container lifecycle commands practiced
- Docker Compose configuration created and validated
- Three microservices started simultaneously with Docker Compose
- Shared Docker network created
- DNS-based service discovery verified
- Container-to-container HTTP communication verified
- Redis added to the Docker Compose environment
- Product Service connected to Redis through Docker networking
- Redis caching implemented
- Cache hit and cache miss behavior verified
- Redis cache TTL implemented and tested
- Redis configuration externalized using environment variables
- `.env` and `.env.example` configuration introduced
- Local `.env` excluded from Git version control
- Redis health check configured
- Redis failure behavior tested
- Product Service fallback behavior verified when Redis is unavailable
- PostgreSQL added to Docker Compose
- PostgreSQL persistent Docker volume configured
- Product database schema created
- Large e-commerce product dataset imported
- 105,542 product records stored in PostgreSQL
- Product Service connected to PostgreSQL
- In-memory Product Service data replaced by PostgreSQL
- Pagination implemented
- Product-name search implemented
- Color filtering implemented
- Redis cache keys adapted for query parameters
- PostgreSQL color index created
- Index usage verified using `EXPLAIN`
- PostgreSQL data persistence verified across container restarts

## Next Steps

The project will be expanded incrementally with:

- AWS RDS PostgreSQL
- Database high availability and Multi-AZ concepts
- AWS Secrets management
- Application Load Balancer and health checks
- Auto Scaling
- Terraform Infrastructure as Code
- Real service-to-service application logic
- Nginx reverse proxy and routing
- Container image optimization
- Multi-stage builds
- Non-root containers
- Dependency and container vulnerability scanning
- Container registry
- GitHub Actions CI/CD
- Frontend development and backend integration
- Kubernetes
- Helm
- Amazon EKS
- Prometheus and Grafana monitoring
- Alerting and observability

## Technologies

Currently used:

- Python
- Flask
- PostgreSQL
- Psycopg
- Redis
- Docker
- Docker Compose
- Git
- GitHub
- VS Code

Planned:

- AWS RDS
- AWS Secrets Management
- AWS Application Load Balancer
- Terraform
- Nginx
- GitHub Actions
- Container Registry
- React
- Kubernetes
- Helm
- Amazon EKS
- Prometheus
- Grafana

## Author

**Merve Cura**

Computer Engineering graduate focusing on Cloud and DevOps technologies.
