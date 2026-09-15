# CloudShop Microservices

CloudShop is a cloud-native e-commerce microservices project built to practice and demonstrate real-world Cloud and DevOps concepts.

The project is being developed incrementally, starting with local microservice development, Docker containerization, and multi-container orchestration. It will later be extended with persistent databases, caching, reverse proxy routing, CI/CD, Kubernetes, cloud deployment, and observability.

## Project Goals

The main goals of this project are to:

- Build an e-commerce backend using a microservices architecture
- Develop independent backend services
- Containerize services with Docker
- Practice Docker networking and service discovery
- Manage multi-container environments with Docker Compose
- Implement service-to-service communication
- Apply CI/CD practices with GitHub Actions
- Deploy containerized workloads to cloud environments
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
   User DB          Product DB         Order DB
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
- **Persistence:** Independent databases and Docker volumes
- **Version control:** Git and GitHub
- **CI/CD:** GitHub Actions
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

The Product Service manages the current product API.

Available endpoints:

```http
GET /health
GET /products
GET /products/<product_id>
```

`GET /products` returns the available products.

`GET /products/<product_id>` returns a specific product based on its ID.

If the requested product does not exist, the API returns:

```text
404 Not Found
```

The service runs on port:

```text
5001
```

Product data is currently stored in memory and will later be moved to persistent storage.

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

For example:

```text
localhost:5001
       |
       v
Host Port 5001
       |
       v
Container Port 5001
       |
       v
Product Service
```

The services were initially built and run individually to verify their Docker configurations before being integrated with Docker Compose.

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

The complete environment can be built and started using:

```bash
docker compose up -d --build
```

Running services can be inspected using:

```bash
docker compose ps
```

Instead of manually building and starting every container, Docker Compose now manages all three services as a single application environment.

## Docker Compose Networking

Docker Compose automatically creates a shared network for the CloudShop services.

Current container architecture:

```text
                  Docker Compose Network
                           |
              +------------+------------+
              |            |            |
              v            v            v
        User Service  Product Service  Order Service
            :5000          :5001          :5002
```

All three containers can communicate through this internal network.

This means services do not need to know each other's dynamically assigned container IP addresses.

## DNS-Based Service Discovery

Docker Compose provides built-in DNS-based service discovery.

Containers can locate other services using their Compose service names.

For example, from inside Order Service:

```text
product-service
```

refers to the Product Service container.

DNS resolution was verified using:

```bash
docker compose exec order-service getent hosts product-service
```

Docker's internal DNS successfully resolved the Product Service name to its container network address.

This avoids relying on hard-coded container IP addresses.

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

## Host Access vs Internal Communication

For local development, the services can currently be accessed from the host machine using:

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
```

Inside the Docker Compose network, containers communicate using service names:

```text
user-service:5000
product-service:5001
order-service:5002
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
              |               ^               |
              |               |               |
              +------ Docker Compose Network--+
```

The current architecture establishes the initial multi-service foundation of CloudShop.

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
- Docker Compose configuration created
- Docker Compose configuration validated
- Three microservices started simultaneously with Docker Compose
- Shared Docker network created
- DNS-based service discovery verified
- Container-to-container HTTP communication verified

## Next Steps

The project will be expanded incrementally with:

- Persistent databases
- Docker volumes
- Redis caching
- Real service-to-service application logic
- Nginx reverse proxy and routing
- Environment variables
- `.env` configuration
- Docker health checks
- Container image optimization
- Multi-stage builds
- Non-root containers
- Secrets management
- Dependency and container vulnerability scanning
- Container registry
- GitHub Actions CI/CD
- Frontend development and backend integration
- Kubernetes
- AWS deployment
- Prometheus and Grafana monitoring
- Alerting and observability

## Technologies

Currently used:

- Python
- Flask
- Docker
- Docker Compose
- Git
- GitHub
- VS Code

Planned:

- Nginx
- Redis
- Databases
- GitHub Actions
- Container Registry
- React
- Kubernetes
- AWS
- Prometheus
- Grafana

## Author

**Merve Cura**

Computer Engineering graduate focusing on Cloud and DevOps technologies.
