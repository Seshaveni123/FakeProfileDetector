# FakeGuard AI — Cloud-Native Social Media Fake Profile Detection System

[![Build Status](https://img.shields.io/badge/CI%2FCD-Jenkins%20Pipeline-blue.svg)](https://github.com/Seshaveni123/FakeProfileDetector)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-seshaveni1-0db7ed.svg?logo=docker&logoColor=white)](https://hub.docker.com/u/seshaveni1)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestration-326CE5.svg?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Microservices-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%2016-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Prometheus](https://img.shields.io/badge/Monitoring-Prometheus-E6522C.svg?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Visualization-Grafana-F46800.svg?logo=grafana&logoColor=white)](https://grafana.com/)
[![Terraform](https://img.shields.io/badge/IaC-AWS%20Terraform-7B42BC.svg?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![License](https://img.shields.io/badge/License-Academic%20%2F%20Educational-lightgrey.svg)](#author-and-project-information)

FakeGuard AI is an enterprise-grade, cloud-native machine learning system engineered to classify social media profiles as **Genuine** or **Fake/Bot**. Designed with a decoupled microservices architecture, the platform features a responsive React single-page application, containerized FastAPI services, persistent PostgreSQL storage, end-to-end automated testing, Jenkins CI/CD automation, Docker Hub image distribution, Kubernetes orchestration with Horizontal Pod Autoscaling (HPA), and full-stack observability powered by Prometheus and Grafana.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Application Workflow](#application-workflow)
- [Machine Learning Models and Prediction Process](#machine-learning-models-and-prediction-process)
- [Project Structure](#project-structure)
- [Prerequisites and Installation](#prerequisites-and-installation)
- [Environment Variables and Configuration](#environment-variables-and-configuration)
- [Running Locally with Docker Compose](#running-locally-with-docker-compose)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Jenkins CI/CD Pipeline](#jenkins-cicd-pipeline)
- [Docker Hub Image Publishing](#docker-hub-image-publishing)
- [Monitoring with Prometheus and Grafana](#monitoring-with-prometheus-and-grafana)
- [API Documentation and Endpoints](#api-documentation-and-endpoints)
- [Testing and Validation](#testing-and-validation)
- [Screenshots and Demo](#screenshots-and-demo)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Future Enhancements](#future-enhancements)
- [Author and Project Information](#author-and-project-information)

---

## Project Overview

Online social networks face widespread challenges from automated bots, sybil accounts, and malicious impersonators that distribute disinformation, manipulate public sentiment, and execute phishing scams. FakeGuard AI delivers an end-to-end detection engine that processes behavioral metadata (such as follower-to-following ratios, username digit density, external link inclusion, and engagement patterns) to generate real-time confidence scores and explainable classification metrics.

Originally developed as a monolithic application, the repository has been refactored into a scalable cloud-native microservices ecosystem:
- **Prediction Service**: Decoupled, stateless machine learning inference engine.
- **History Service**: Persistence layer managing PostgreSQL transactional scan records.
- **Analytics Service**: Aggregation microservice computing system-wide detection metrics.
- **Frontend SPA**: React 18 interface with real-time analytics, risk indicators, and batch CSV processing.
- **Infrastructure as Code**: Terraform configurations provisioning modular AWS VPC, EC2, S3, and IAM architectures.

---

## Problem Statement

Detecting fraudulent social media accounts manually is infeasible given the scale and velocity of content creation. Traditional rule-based heuristics fail against adaptive bot behaviors. Key operational challenges include:
1. **Asymmetric Feature Spaces**: Different social networks exhibit distinct metadata footprints (e.g., Instagram bio/privacy vs. Twitter retweet/mention counts).
2. **System Scalability**: Handling variable traffic spikes during large-scale scanning operations without service degradation.
3. **Operational Visibility**: Maintaining visibility into model latency, error rates, system throughput, and resource saturation in distributed environments.
4. **Automated Delivery**: Ensuring rapid, defect-free deployments from code commit to containerized Kubernetes rollouts.

---

## Objectives

- Develop specialized machine learning classifiers trained on real-world Instagram and Twitter profile distributions.
- Deconstruct the backend into single-responsibility, stateless microservices communicating via asynchronous and HTTP protocols.
- Guarantee zero data loss using persistent volume claims backed by PostgreSQL.
- Build an automated Jenkins declarative CI/CD pipeline enforcing static validation, unit testing, Docker builds, Docker Hub publishing, and Kubernetes deployments.
- Configure Horizontal Pod Autoscalers (HPA) to scale pods based on CPU utilization dynamically.
- Implement comprehensive telemetry with Prometheus metric endpoints and a custom Grafana operations dashboard.
- Provide Infrastructure as Code (IaC) blueprints using Terraform to facilitate cloud deployment on AWS.

---

## Key Features

- **Multi-Platform Classification**: Dedicated inspection workflows tailored for Instagram and Twitter/X account metadata.
- **Real-Time Single Profile Scan**: Immediate inference returning classification labels (`Fake` vs. `Real`), probability percentages, and categorical risk levels (`High`, `Moderate`, `Low`).
- **Explainable AI (XAI) Indicators**: Dynamic attribution detailing specific risk drivers (e.g., zero profile picture, excessive username numbers, extreme follow ratios).
- **Bulk CSV Batch Processing**: Asynchronous batch scanning capable of evaluating hundreds of profile records simultaneously with downloadable results.
- **System Analytics Dashboard**: High-level telemetry tracking total scans, fake ratio percentages, platform distribution charts, and risk spectrums.
- **Decoupled Microservice Architecture**: Stateless inference pods backed by an independent history microservice and relational database.
- **Automated CI/CD Pipeline**: Declarative 9-stage Jenkins automation featuring automated tests, Docker Hub registry publishing, and Kubernetes rollout verification.
- **Production Observability**: Prometheus scraping endpoints exposing service-level metrics (`predictions_total`, `requests_total`, `request_duration_seconds`) visualized through Grafana.

---

## System Architecture

FakeGuard AI uses a modern, containerized microservices architecture deployed to Kubernetes. External traffic flows through an Ingress controller or reverse proxy directly into the frontend and backend microservices.

```mermaid
flowchart TD
    subgraph ClientLayer["Client Layer"]
        User["User / Browser"]
    end

    subgraph IngressGateway["Ingress / Gateway Layer"]
        Ingress["Nginx Ingress / Vite Reverse Proxy<br/>Port 5173 / 80"]
    end

    subgraph ApplicationServices["Kubernetes Pods (Namespace: fakeguard)"]
        Frontend["Frontend SPA<br/>(React 18 + Vite)<br/>Port 5173"]
        
        PredictionSvc["Prediction Service<br/>(FastAPI Replicas: 2)<br/>Port 8000"]
        HistorySvc["History Service<br/>(FastAPI Replicas: 2)<br/>Port 8001"]
        AnalyticsSvc["Analytics Service<br/>(FastAPI Replicas: 2)<br/>Port 8002"]
        
        MLModels[("Serialized ML Models<br/>XGBoost / Random Forest")]
        PostgresDB[("PostgreSQL 16 Database<br/>Port 5432<br/>PVC: fakeguard-postgres-data")]
    end

    subgraph Observability["Monitoring Namespace"]
        Prometheus["Prometheus Server<br/>Port 9090"]
        Grafana["Grafana Dashboards<br/>Port 3000"]
    end

    %% Client Routing
    User --> Ingress
    Ingress -->|/| Frontend
    Ingress -->|/api/predict| PredictionSvc
    Ingress -->|/api/history| HistorySvc
    Ingress -->|/api/dashboard| AnalyticsSvc

    %% Internal Service Mesh Communication
    Frontend -.->|Proxy Fallback| PredictionSvc
    Frontend -.->|Proxy Fallback| HistorySvc
    Frontend -.->|Proxy Fallback| AnalyticsSvc

    PredictionSvc --> MLModels
    PredictionSvc -->|HTTP POST /records| HistorySvc
    AnalyticsSvc -->|HTTP GET /history| HistorySvc
    HistorySvc -->|psycopg SQL| PostgresDB

    %% Observability Scrapes
    Prometheus -.->|Scrape :8000/metrics| PredictionSvc
    Prometheus -.->|Scrape :8001/metrics| HistorySvc
    Prometheus -.->|Scrape :8002/metrics| AnalyticsSvc
    Grafana -->|PromQL| Prometheus
```

### Verified Service Ports

| Service Component | Internal Port | Host / Node Port | Primary Protocol | Role / Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | `5173` | `5173` | HTTP | React 18 single-page application & Vite proxy |
| **Prediction Service** | `8000` | `8000` | HTTP / REST | Model inference, validation, and feature scaling |
| **History Service** | `8001` | `8001` | HTTP / REST | Transactional storage and history CRUD operations |
| **Analytics Service** | `8002` | `8002` | HTTP / REST | Metric aggregation and dashboard summaries |
| **PostgreSQL** | `5432` | `5432` | PostgreSQL | Relational persistence for scan records |
| **Prometheus** | `9090` | `9090` | HTTP | Time-series metric collection and PromQL engine |
| **Grafana** | `80` | `3000` / `3001` | HTTP | Operational visualization and telemetry dashboards |

---

## Technology Stack

### Application & Machine Learning

- **Core Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11) with Uvicorn ASGI server
- **ML Frameworks**: [scikit-learn](https://scikit-learn.org/), [XGBoost](https://xgboost.readthedocs.io/), NumPy, Pandas
- **Frontend Architecture**: [React 18](https://react.dev/), [Vite](https://vitejs.dev/), CSS3 with custom Glassmorphism tokens
- **Database**: [PostgreSQL 16 Alpine](https://www.postgresql.org/) with `psycopg` connection driver
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/) schema enforcement
- **Testing**: [pytest](https://docs.pytest.org/), `pytest-asyncio`, `httpx` TestClient

### DevOps, Cloud & CI/CD

- **Containerization**: [Docker](https://www.docker.com/) with multi-stage production Dockerfiles
- **Container Registry**: [Docker Hub](https://hub.docker.com/) (`seshaveni1` repository namespace)
- **Container Orchestration**: [Kubernetes](https://kubernetes.io/) (Deployments, ClusterIP Services, PVC, HPA, Ingress)
- **CI/CD Automation**: [Jenkins](https://www.jenkins.io/) Declarative Pipelines running inside Docker
- **Monitoring & Metrics**: [Prometheus](https://prometheus.io/) Operator (`kube-prometheus-stack`) with custom ServiceMonitors
- **Telemetry Dashboards**: [Grafana](https://grafana.com/) with provisioned `FakeGuard AI Monitoring` dashboard
- **Infrastructure as Code**: [Terraform](https://www.terraform.io/) targeting AWS (`ap-south-1`)

---

## Application Workflow

1. **User Request**: The operator inputs profile metadata via the React UI or sends a POST request to `/api/predict`.
2. **Schema Sanitization**: The Prediction Service verifies input ranges, handles aliases, and assigns defaults using Pydantic.
3. **Feature Preprocessing**: Numerical inputs are vectorized into platform-specific feature arrays matching training schemas.
4. **Model Inference**: The active machine learning pipeline evaluates the feature vector and outputs prediction probabilities.
5. **Decoupled Persistence**: The Prediction Service sends an asynchronous HTTP record creation request to the History Service (`POST /records`).
6. **Relational Storage**: The History Service writes the prediction result, platform, timestamp, and risk evaluation into PostgreSQL.
7. **Client Response**: The client receives classification outcomes, probability scores, risk flags, and explainability summaries.
8. **Telemetry Emission**: Background middleware increments operational Prometheus counters (`predictions_total`, `predictions_fake`, `predictions_real`).

---

## Machine Learning Models and Prediction Process

FakeGuard AI maintains distinct, specialized models trained on real-world datasets rather than using a one-size-fits-all heuristic.

### 1. Instagram Profile Classifier

- **Primary Algorithm**: **XGBoost Classifier** (Selected as the best-performing model over Random Forest)
- **Dataset Size**: 5,052 total samples (4,041 training, 1,011 test)
- **Model Accuracy**: **98.32%**
- **Evaluation Metrics**:
  - Precision: **0.9899**
  - Recall: **0.9761**
  - F1-Score: **0.9830**
  - AUC-ROC: **0.9989**
- **Feature Schema (11 Inputs)**:
  1. `profile pic` (Binary presence)
  2. `nums/length username` (Ratio of digits to username length)
  3. `fullname words` (Word count in full name)
  4. `nums/length fullname` (Ratio of digits to full name length)
  5. `name==username` (Binary equality match)
  6. `description length` (Bio character count)
  7. `external URL` (Binary flag for bio link)
  8. `private` (Account privacy status)
  9. `#posts` (Media count)
  10. `#followers` (Follower count)
  11. `#follows` (Following count)
- **Feature Importance**: Profile Picture presence is the dominant signal (**0.8390**), followed by Username Digit Ratio (**0.0659**) and Follower Count (**0.0226**).

### 2. Twitter / X Profile Classifier

- **Algorithm**: **Random Forest Classifier** & **XGBoost**
- **Dataset Size**: 50,000 total samples (40,000 training, 10,000 test)
- **Feature Schema (4 Inputs)**:
  1. `Retweet Count` (Average retweets received)
  2. `Mention Count` (Average user mentions)
  3. `Follower Count` (Audience reach)
  4. `Verified` (Verification badge status)
- **Feature Importance**: Follower Count accounts for **0.6291** of model weight, followed by Retweet Count (**0.2728**) and Mention Count (**0.0678**).
- **Engineering Transparency**: The Twitter dataset exhibits high entropy across public bot datasets. The model evaluation includes stratified 5-fold cross-validation and benchmark comparisons against majority-class baselines documented in `backend/models/twitter_metadata.json`.

---

## Project Structure

```text
FakeProfileDetector-Git/
├── .gitignore
├── Jenkinsfile                  # 9-stage declarative CI/CD pipeline definition
├── README.md                    # Root project documentation
├── docker-compose.yml           # Multi-container local orchestration configuration
├── requirements.txt             # Global Python dependency manifest
├── sample_bulk_test.csv         # Sample Instagram dataset for batch verification
├── sample_twitter_bulk.csv      # Sample Twitter dataset for batch verification
├── backend/                     # Compatibility assets and model binaries
│   └── models/                  # Serialized models, scalers, and metadata JSON
│       ├── insta_model.pkl
│       ├── insta_scaler.pkl
│       ├── insta_metadata.json
│       ├── twitter_model.pkl
│       ├── twitter_scaler.pkl
│       └── twitter_metadata.json
├── database/                    # SQL schema definitions
│   └── schema.sql
├── frontend/                    # React 18 single-page application
│   ├── Dockerfile               # Multi-stage production container build
│   ├── package.json             # NPM package dependencies
│   ├── vite.config.js           # Vite dev server and proxy definitions
│   └── src/                     # React application source code
│       ├── App.jsx              # Main UI component with tab navigation
│       ├── index.css            # Custom CSS styling tokens
│       └── main.jsx             # React entry point
├── kubernetes/                  # Production Kubernetes resource manifests
│   ├── namespace.yaml           # Namespace declaration (fakeguard)
│   ├── microservices.yaml       # Deployments, Services, and HPA for backend & DB
│   ├── frontend-deployment.yaml # Frontend Deployment configuration
│   ├── frontend-service.yaml    # Frontend ClusterIP Service
│   ├── frontend-hpa.yaml        # Frontend Horizontal Pod Autoscaler
│   ├── ingress.yaml             # Nginx Ingress routing rules
│   ├── servicemonitors.yaml     # Prometheus Operator ServiceMonitors
│   └── grafana-dashboard.yaml   # ConfigMap containing operational Grafana dashboard
├── ml/                          # Machine learning training scripts
│   └── train_models.py          # Data ingestion, preprocessing, and training pipeline
├── services/                    # Cloud-native microservices
│   ├── README.md                # Microservices architecture guide
│   ├── prediction-service/      # ML inference FastAPI microservice (Port 8000)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app.py
│   ├── history-service/         # PostgreSQL persistence microservice (Port 8001)
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app.py
│   └── analytics-service/       # Metric aggregation microservice (Port 8002)
│       ├── Dockerfile
│       ├── requirements.txt
│       └── app.py
├── terraform/                   # AWS Infrastructure as Code (IaC) specifications
│   ├── main.tf                  # VPC, subnets, route tables, security groups, EC2
│   ├── s3.tf                    # Encrypted private S3 bucket configuration
│   ├── iam.tf                   # Least-privilege IAM roles and instance profiles
│   ├── variables.tf             # Configurable input variables
│   ├── outputs.tf               # Infrastructure outputs
│   └── terraform.tfvars.example # Example variable definitions
└── tests/                       # Automated test suites
    ├── test_api.py              # Microservice endpoint integration tests
    ├── test_analytics_service.py# Analytics calculation test suite
    ├── test_prediction_bulk.py  # Batch CSV upload validation
    └── test_twitter_pipeline.py # Twitter preprocessing and inference tests
```

---

## Prerequisites and Installation

### Software Requirements

- **Operating System**: Linux, macOS, or Windows 10/11 (with WSL2 enabled)
- **Python**: Version `3.11` or newer
- **Node.js**: Version `18.x` or newer (with `npm`)
- **Docker Engine**: Version `24.x` or newer with Docker Compose v2
- **Kubernetes CLI (`kubectl`)**: Version `1.28` or newer (Docker Desktop Kubernetes or Minikube)
- **Git**: Version `2.x`

### 1. Clone the Repository

```bash
git clone https://github.com/Seshaveni123/FakeProfileDetector.git
cd FakeProfileDetector
```

### 2. Python Virtual Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Upgrade pip and install test dependencies
pip install --upgrade pip
pip install -r services/prediction-service/requirements.txt
pip install -r services/history-service/requirements.txt
pip install -r services/analytics-service/requirements.txt
pip install pytest httpx
```

### 3. Frontend Installation

```bash
cd frontend
npm install
cd ..
```

---

## Environment Variables and Configuration

FakeGuard AI uses environment variables to configure database connections and service discovery. For local development, create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_DB=fakeguard
POSTGRES_USER=fakeguard
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://fakeguard:your_secure_password_here@postgres:5432/fakeguard

# Service Discovery
HISTORY_SERVICE_URL=http://history-service:8001
PREDICTION_SERVICE_URL=http://prediction-service:8000
ANALYTICS_SERVICE_URL=http://analytics-service:8002

# Inference Configuration
MODEL_DIR=./backend/models
HISTORY_REQUEST_TIMEOUT_SECONDS=5.0
```

> **Security Note**: Never commit live `.env` files containing actual passwords or credentials to version control. The repository `.gitignore` automatically excludes `.env` and credential files.

---

## Running Locally with Docker Compose

Docker Compose builds and orchestrates all five services (PostgreSQL, History, Prediction, Analytics, and Frontend) with health checks and volume persistence:

```bash
# Build and start all services in the background
docker compose up --build -d

# Check running container health status
docker compose ps

# Tail logs across all services
docker compose logs -f
```

### Accessing Local Services

- **Frontend Application**: [http://localhost:5173](http://localhost:5173)
- **Prediction Service OpenAPI / Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **History Service OpenAPI / Swagger**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Analytics Service OpenAPI / Swagger**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **PostgreSQL Database**: `localhost:5432` (`fakeguard` database)

```bash
# Graceful shutdown and volume preservation
docker compose down

# To reset database volumes completely (Caution: erases local scan history):
docker compose down -v
```

---

## Kubernetes Deployment

The application manifests are located in the [kubernetes/](kubernetes/) directory and deploy into the isolated `fakeguard` namespace.

### 1. Ensure Kubernetes Cluster is Active

Verify that your Kubernetes cluster (Docker Desktop, Minikube, or cloud cluster) is operational:

```bash
kubectl cluster-info
```

### 2. Create the Namespace & Database Secret

Create the `fakeguard` namespace and generate the required database secret:

```bash
# Apply namespace
kubectl apply -f kubernetes/namespace.yaml

# Generate the database secret (replace with your secure password)
kubectl create secret generic fakeguard-database \
  --namespace=fakeguard \
  --from-literal=database=fakeguard \
  --from-literal=username=fakeguard \
  --from-literal=password='your_secure_password_here' \
  --from-literal=url='postgresql://fakeguard:your_secure_password_here@postgres-service:5432/fakeguard' \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 3. Deploy Storage, Microservices, and Frontend

```bash
# Deploy PostgreSQL, Prediction, History, Analytics Services, and HPA
kubectl apply -n fakeguard -f kubernetes/microservices.yaml

# Deploy Frontend Application and Service
kubectl apply -n fakeguard -f kubernetes/frontend-deployment.yaml
kubectl apply -n fakeguard -f kubernetes/frontend-service.yaml

# Optional: Deploy Ingress controller rules (if ingress-nginx is installed)
kubectl apply -n fakeguard -f kubernetes/ingress.yaml
```

### 4. Verify Rollout Status and Pod Health

```bash
# Confirm all pods are Running and Ready (1/1)
kubectl get pods -n fakeguard -o wide

# Check services and ClusterIP endpoints
kubectl get svc -n fakeguard

# Check Horizontal Pod Autoscalers (HPA)
kubectl get hpa -n fakeguard
```

### 5. Accessing the Application via Port-Forward

To access the frontend and microservices without an Ingress controller:

```bash
# Frontend UI
kubectl port-forward -n fakeguard service/frontend-service 5173:5173

# Prediction Service API
kubectl port-forward -n fakeguard service/prediction-service 8000:8000

# Analytics Service API
kubectl port-forward -n fakeguard service/analytics-service 8002:8002
```

---

## Jenkins CI/CD Pipeline

The project includes a production-grade Jenkins declarative pipeline defined in [Jenkinsfile](Jenkinsfile). The pipeline automates the complete lifecycle from source checkout to verified Kubernetes deployment.

```mermaid
flowchart LR
    Stage1["1. Checkout<br/>Git SCM"] --> Stage2["2. Validation<br/>Syntax & Docker"]
    Stage2 --> Stage3["3. Testing<br/>pytest Unit Tests"]
    Stage3 --> Stage4["4. Build<br/>Docker Multi-Image"]
    Stage4 --> Stage5["5. Publish<br/>Docker Hub Push"]
    Stage5 --> Stage6["6. K8s Validation<br/>Manifest Dry-Run"]
    Stage6 --> Stage7["7. K8s Deploy<br/>Apply fakeguard"]
    Stage7 --> Stage8["8. Rollout<br/>Verify Health"]
    Stage8 --> Stage9["9. Cleanup<br/>Prune Cache"]
```

### Pipeline Stages Breakdown

1. **Stage 1: Checkout Source Code**: Clones the GitHub repository and records the Git commit SHA.
2. **Stage 2: Validation**: Validates the presence of Dockerfiles, Compose specs, and Kubernetes manifests, and checks Docker daemon connectivity.
3. **Stage 3: Automated Testing**: Executes automated test suites (`pytest tests/`) covering prediction endpoints, analytics aggregations, and feature pipelines.
4. **Stage 4: Docker Build**: Builds all four application Docker images with parallel tag targets (`${BUILD_NUMBER}` and `latest`).
5. **Stage 5: Publish to Docker Hub**: Securely authenticates with Docker Hub using Jenkins credentials ID `dockerhub`, publishes all 4 images with retry fault-tolerance, and executes `docker logout`.
6. **Stage 6: Kubernetes Validation**: Executes client-side dry-run validation (`kubectl apply --dry-run=client`) across all manifest files.
7. **Stage 7: Kubernetes Deployment**: Creates the `fakeguard` namespace, ensures the database Secret exists, and applies deployments, services, and HPAs.
8. **Stage 8: Rollout Verification**: Validates successful rollout status across all deployments (`postgres`, `prediction`, `history`, `analytics`, `frontend`) within a 90-second timeout threshold.
9. **Stage 9: Post-Build Cleanup**: Prunes dangling Docker build cache and logs execution metrics.

---

## Docker Hub Image Publishing

All application Docker images are published to Docker Hub under the verified namespace `seshaveni1`. Images are dual-tagged with both the explicit Jenkins build number and `latest`.

| Image Repository | Build Context | Dockerfile Path | Tags Available |
| :--- | :--- | :--- | :--- |
| [`seshaveni1/fakeguard-prediction`](https://hub.docker.com/r/seshaveni1/fakeguard-prediction) | `.` (Root) | `services/prediction-service/Dockerfile` | `latest`, `10` |
| [`seshaveni1/fakeguard-history`](https://hub.docker.com/r/seshaveni1/fakeguard-history) | `.` (Root) | `services/history-service/Dockerfile` | `latest`, `10` |
| [`seshaveni1/fakeguard-analytics`](https://hub.docker.com/r/seshaveni1/fakeguard-analytics) | `.` (Root) | `services/analytics-service/Dockerfile` | `latest`, `10` |
| [`seshaveni1/fakeguard-frontend`](https://hub.docker.com/r/seshaveni1/fakeguard-frontend) | `./frontend` | `frontend/Dockerfile` | `latest`, `10` |

*Note: PostgreSQL uses the official upstream `postgres:16-alpine` image and is deliberately not published under custom credentials.*

---

## Monitoring with Prometheus and Grafana

FakeGuard AI includes cloud-native monitoring configured via Prometheus and Grafana (using the `kube-prometheus-stack` Helm chart).

### 1. Prometheus Telemetry

Microservices expose Prometheus-compatible metrics on `/metrics`:
- `predictions_total{platform="instagram|twitter"}`: Cumulative profile scans executed.
- `predictions_fake`: Count of profiles classified as fraudulent or bots.
- `predictions_real`: Count of profiles classified as authentic.
- `requests_total`: Total HTTP requests processed per microservice.
- `errors_total`: Count of HTTP 4xx/5xx error responses.
- `request_duration_seconds_sum` / `request_duration_seconds_count`: Request latency tracking.

ServiceMonitors for Prometheus scraping are defined in [kubernetes/servicemonitors.yaml](kubernetes/servicemonitors.yaml).

### 2. Grafana Operations Dashboard

A provisioned dashboard titled **FakeGuard AI Monitoring** is defined in [kubernetes/grafana-dashboard.yaml](kubernetes/grafana-dashboard.yaml) and tracks:
- **Total Predictions Count**: Real-time counter of platform scans.
- **Fake vs. Real Detection Split**: Visual breakdown of detection outcomes.
- **CPU & Memory Utilization**: Per-pod resource consumption and threshold limits.
- **Pod Replicas & HPA Status**: Active replica counts versus target capacities.
- **Service Request Latency**: P95/P99 latency trends.

```bash
# Port-forward Grafana to localhost (monitoring namespace)
kubectl port-forward -n monitoring service/monitoring-grafana 3000:80

# Port-forward Prometheus server
kubectl port-forward -n monitoring service/monitoring-kube-prometheus-prometheus 9090:9090
```

---

## API Documentation and Endpoints

### 1. Prediction Service (`http://localhost:8000`)

| Method | Endpoint | Description | Request Payload / Params |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Health check & model metadata | None |
| `POST` | `/predict` | Single profile classification | JSON (`PredictionRequest`) |
| `POST` | `/predict/bulk` | Bulk CSV batch processing | Multi-part Form (`file`, `platform`) |
| `GET` | `/model-info` | Algorithm metadata and schemas | Query (`platform=instagram\|twitter`) |
| `GET` | `/metrics` | Prometheus telemetry metrics | None |

#### Sample `/predict` Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "username": "suspicious_user_9921",
    "profile_pic": 0,
    "nums_length_username": 0.45,
    "fullname_words": 1,
    "nums_length_fullname": 0.0,
    "name_eq_username": 0,
    "description_length": 0,
    "external_url": 0,
    "private": 0,
    "posts_count": 2,
    "followers_count": 15,
    "following_count": 890
  }'
```

#### Sample `/predict` Response

```json
{
  "platform": "instagram",
  "prediction": 1,
  "label": "Fake",
  "probability": 94.2,
  "risk_level": "High",
  "confidence": "High",
  "model_used": "XGBoost",
  "explanation": "High risk of fake profile. Strong indicators: Missing profile picture, High ratio of numbers in username, Extreme following-to-follower ratio.",
  "timestamp": "2026-10-15T13:48:35.120Z"
}
```

### 2. History Service (`http://localhost:8001`)

| Method | Endpoint | Description | Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Service health status | None |
| `POST` | `/records` | Record a prediction (Internal API) | JSON (`RecordCreateRequest`) |
| `GET` | `/history` | Paginated scan history | Query (`limit=50`, `offset=0`) |
| `DELETE` | `/history/clear` | Clear scan history | None |
| `GET` | `/metrics` | Prometheus telemetry metrics | None |

### 3. Analytics Service (`http://localhost:8002`)

| Method | Endpoint | Description | Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Service health status | None |
| `GET` | `/dashboard` | Aggregated analytics & distribution | None |
| `GET` | `/metrics` | Prometheus telemetry metrics | None |

---

## Testing and Validation

The automated test suite in [tests/](tests/) validates the platform without requiring external network connectivity or live cloud resources:

```bash
# Run the complete test suite with verbose output
pytest tests/ -v --ignore=tests/test_microservices_e2e.py
```

### Test Coverage Highlights

- `tests/test_api.py`: Validates FastAPI routing, CORS headers, model loading, and schema validation.
- `tests/test_prediction_bulk.py`: Tests CSV parsing, alias normalization, and error handling for malformed bulk uploads.
- `tests/test_twitter_pipeline.py`: Verifies feature extraction, scaling, and inference integrity for Twitter profiles.
- `tests/test_analytics_service.py`: Tests metric aggregation, percentage calculations, and fallback handling when history is empty.

---

## Screenshots and Demo

When running the application locally at `http://localhost:5173`, the React web application provides five interactive views:

1. **Single Profile Scan**: Interactive form with real-time risk gauges, platform selectors (Instagram & Twitter), and explainability breakdowns.
2. **Bulk CSV Scanner**: Drag-and-drop CSV upload supporting batch evaluations with downloadable results. Use `sample_bulk_test.csv` or `sample_twitter_bulk.csv` for demonstration.
3. **Analytics Dashboard**: Dynamic charts displaying total scans, fake vs. genuine proportions, risk distributions, and platform breakdowns.
4. **Detection History**: Paginated, filterable table of past scans with search and record clearance controls.
5. **Model Information**: Live transparency tab detailing training datasets, feature importance bars, accuracy benchmarks, and confusion matrices.

*(To add project screenshots to your repository, save PNG captures into an `assets/` folder and link them using relative markdown syntax).*

---

## Troubleshooting

### 1. Frontend Shows "Backend service is unavailable"

- **Cause**: The backend microservices are either starting up or port 8000/8001/8002 is not reachable.
- **Fix**: Check container health with `docker compose ps` or pod status with `kubectl get pods -n fakeguard`. Verify Vite proxy routes in `frontend/vite.config.js`.

### 2. Database Connection Error in History Service

- **Cause**: PostgreSQL is not yet ready to accept connections or credentials in `fakeguard-database` secret do not match.
- **Fix**: Check database logs:
  ```bash
  kubectl logs -n fakeguard deployment/postgres-deployment
  ```
  Ensure the secret exists and contains valid `database`, `username`, `password`, and `url` keys.

### 3. Prometheus Target Shows "DOWN"

- **Cause**: ServiceMonitor selector labels do not match the target service labels or port names differ.
- **Fix**: Inspect `kubernetes/servicemonitors.yaml`. Ensure service definitions include `labels: {app: <service-name>}` and port name `http`.

---

## Security Considerations

- **Credential Management**: Database secrets and Docker Hub tokens are never committed to version control. Passwords in Kubernetes are managed via Kubernetes Secrets.
- **Principle of Least Privilege**: In the Terraform specifications ([terraform/iam.tf](terraform/iam.tf)), IAM policies restrict EC2 access strictly to designated S3 model buckets with read-only permissions.
- **Network Isolation**: In Kubernetes, database access is restricted to cluster-internal traffic (`postgres-service` uses `ClusterIP` and is not exposed to the public internet).
- **Input Sanitization**: Pydantic models strictly validate all incoming API payloads, preventing injection attacks and buffer overflows.
- **Token Masking**: The Jenkins CI/CD pipeline uses `withCredentials` to mask secrets (`****`) in build logs and executes `docker logout` after publishing.

---

## Future Enhancements

- [ ] **Transformer-Based NLP Analysis**: Integrate lightweight BERT/RoBERTa models to evaluate user bio semantics and post sentiment.
- [ ] **Live Social API Connectors**: Optional direct OAuth integration with the Twitter/X and Instagram Graph APIs for one-click handle scanning.
- [ ] **Multi-Tenant Authentication**: Role-based access control (RBAC) powered by OAuth2 / JWT for team workspaces.
- [ ] **Automated Retraining Pipeline**: Scheduled Kubeflow / Airflow pipelines to retrain models on freshly labelled drift data.
- [ ] **Helm Chart Packaging**: Package the entire FakeGuard AI Kubernetes deployment into a unified, versioned Helm chart.

---

## Author and Project Information

- **Project Lead & Developer**: **Seshaveni Veeramreddy**
- **GitHub Repository**: [https://github.com/Seshaveni123/FakeProfileDetector](https://github.com/Seshaveni123/FakeProfileDetector)
- **Docker Hub Namespace**: [https://hub.docker.com/u/seshaveni1](https://hub.docker.com/u/seshaveni1)
- **Academic / Portfolio Submission**: Developed as a comprehensive cloud-native machine learning and DevOps capstone project demonstrating end-to-end full-stack engineering, microservice decomposition, CI/CD automation, and Kubernetes orchestration.

---
*FakeGuard AI is maintained for academic and educational evaluation.*
