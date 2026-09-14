# CloudShop Microservices

CloudShop is a cloud-native e-commerce microservices project built to practice and demonstrate real-world Cloud and DevOps concepts.

The project is being developed incrementally, starting with local microservice development and Docker containerization. It will later be extended with multi-container orchestration, CI/CD, Kubernetes, cloud deployment, and observability.

## Project Goals

The main goals of this project are to:

- Build an e-commerce backend using a microservices architecture
- Containerize independent services with Docker
- Practice Docker networking and service discovery
- Implement multi-container environments with Docker Compose
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
      +-------+-------+-------+
      |               |       |
      v               v       v
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

Each stage will be implemented incrementally rather than added only as documentation.

## Current Project Structure

```text
cloudshop-microservices/
|
├── services/
│   └── user-service/
│       ├── app.py
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .dockerignore
│
├── nginx/
│
└── README.md
```

## User Service

The first microservice implemented in the project is the **User Service**.

It is currently a minimal Flask API used to establish the development and containerization workflow.

### Health Endpoint

The service provides a health check endpoint:

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

The health endpoint can later be used by container orchestration platforms, load balancers, and monitoring systems to verify service availability.

## Local Development

A Python virtual environment is used to isolate project dependencies during local development.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the User Service locally:

```bash
python app.py
```

The service becomes available at:

```text
http://localhost:5000
```

Health check:

```text
http://localhost:5000/health
```

## Docker

The User Service has been containerized using Docker.

### Build the Image

From the `services/user-service` directory:

```bash
docker build -t cloudshop-user-service:v1 .
```

The resulting image:

```text
cloudshop-user-service:v1
```

### Run the Container

```bash
docker run -d \
  --name cloudshop-user-container \
  -p 5000:5000 \
  cloudshop-user-service:v1
```

For Windows PowerShell, the command can also be executed on a single line:

```powershell
docker run -d --name cloudshop-user-container -p 5000:5000 cloudshop-user-service:v1
```

The port mapping exposes the Flask application running on port `5000` inside the container through port `5000` on the host machine.

```text
Host                         Docker Container
localhost:5000  ---------->  Flask :5000
```

## Docker Operations Practiced

The following Docker operations have been practiced with the User Service:

```bash
docker build
docker images
docker run
docker ps
docker ps -a
docker logs
docker stop
docker start
```

The container was validated using both its runtime status and the `/health` endpoint.

## Dockerfile

The current User Service Dockerfile:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

This Dockerfile demonstrates:

- Base images
- Working directories
- Build context
- File copying
- Dependency installation
- Image layers and build cache
- Container ports
- Runtime commands

## Docker Ignore

A `.dockerignore` file is used to prevent unnecessary local files from being included in the Docker build context.

Current configuration:

```text
.venv
__pycache__
*.pyc
.git
.gitignore
```

This prevents the local Python virtual environment and other unnecessary files from being copied into the Docker build context.

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
Cloud / Kubernetes (planned)
```

AWS infrastructure is intended to be used as a deployment environment rather than as the primary development workstation.

## Current Progress

Completed:

- Initial microservices architecture defined
- Repository structure created
- Local Python development environment configured
- First Flask microservice created
- `/health` endpoint implemented and tested
- Python dependencies documented with `requirements.txt`
- `.dockerignore` configured
- User Service Dockerfile created
- Docker image successfully built
- Docker container successfully started
- Port mapping tested
- Container logs inspected
- Container lifecycle commands practiced
- Containerized health endpoint successfully tested
- Initial User Service committed and pushed to GitHub

## Next Steps

The project will be expanded incrementally with:

- Product Service
- Order Service
- Docker Compose
- Inter-service networking and DNS
- Redis caching
- Persistent databases and Docker volumes
- Nginx reverse proxy
- Environment variables and secrets management
- Container image optimization
- Container security practices
- Container registry
- GitHub Actions CI/CD
- Kubernetes
- Cloud deployment
- Prometheus and Grafana monitoring

## Technologies

Currently used:

- Python
- Flask
- Docker
- Git
- GitHub
- VS Code

Planned:

- Docker Compose
- Nginx
- Redis
- GitHub Actions
- Kubernetes
- AWS
- Prometheus
- Grafana

## Author

**Merve Cura**

Computer Engineering graduate focusing on Cloud and DevOps technologies.
