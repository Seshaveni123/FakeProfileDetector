# FakeGuard AI — Cloud-Native Fake Profile Detection Web App

<<<<<<< HEAD
FakeGuard AI is a full-stack machine learning project for detecting fake social media profiles on Instagram and Twitter/X.
It includes a FastAPI backend, a React + Vite frontend, separate trained models for each platform, SQLite-based prediction
history, bulk CSV scanning, dashboard analytics, and model metadata views.
=======
## Overview
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

FakeGuard AI is an AI-powered fake profile detection web application designed to classify social media profiles as **Fake** or **Genuine** using Machine Learning models like **Random Forest** and **XGBoost**.

<<<<<<< HEAD
- Platform selector for Instagram and Twitter/X
- Separate ML models for each platform
- Single-profile prediction with fake probability and risk level
- Human-readable explanations for predictions
- Feature importance display from trained model metadata
- Bulk CSV upload for batch profile checks
- Prediction history stored in local SQLite
- Dashboard with scan totals, fake/real counts, platform breakdown, and risk distribution
- Prometheus-style metrics endpoint at `/metrics`
- Docker, Kubernetes, Jenkins, and Terraform assets included
=======
The project integrates **Machine Learning, Full Stack Development, DevOps, Cloud Computing, and Kubernetes orchestration** to build a scalable and production-ready application.
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

---

<<<<<<< HEAD
| Area | Tools |
| --- | --- |
| Backend | FastAPI, Uvicorn, Pydantic |
| Machine Learning | scikit-learn, XGBoost, pandas, NumPy |
| Frontend | React 18, Vite, CSS |
| Database | SQLite |
| Testing | pytest, FastAPI TestClient |
| DevOps | Docker, Docker Compose, Kubernetes, Jenkins, Terraform |
=======
# Features
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

* Fake vs Genuine profile prediction
* Machine Learning based classification
* React.js frontend
* FastAPI backend APIs
* Docker containerization
* Jenkins CI/CD automation
* Kubernetes deployment
* Horizontal Pod Autoscaling (HPA)
* Ingress-based routing
* AWS infrastructure provisioning using Terraform
* Monitoring with Prometheus & Grafana

---

# Tech Stack

## Frontend

* React.js
* HTML
* CSS
* JavaScript

## Backend

* FastAPI
* Python

## Machine Learning

* Random Forest
* XGBoost
* Scikit-Learn
* Pandas
* NumPy

## DevOps & Cloud

* Docker
* Jenkins
* Kubernetes
* Terraform
* AWS
* Git & GitHub

## Monitoring

* Prometheus
* Grafana

---

# Architecture Workflow

```text
<<<<<<< HEAD
FakeProfileDetector1/
|-- backend/
|   |-- app.py
|   |-- requirements.txt
|   |-- Dockerfile
|   |-- predictions.db
|   `-- models/
|       |-- insta_model.pkl
|       |-- insta_scaler.pkl
|       |-- insta_metadata.json
|       |-- twitter_model.pkl
|       |-- twitter_scaler.pkl
|       `-- twitter_metadata.json
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- main.jsx
|   |   `-- index.css
|   |-- package.json
|   |-- vite.config.js
|   `-- Dockerfile
|-- ml/
|   `-- train_models.py
|-- database/
|   `-- schema.sql
|-- data/
|   |-- sample_instagram_bulk.csv
|   `-- sample_twitter_bulk.csv
|-- kubernetes/
|   |-- backend-deployment.yaml
|   |-- backend-service.yaml
|   |-- backend-hpa.yaml
|   |-- frontend-deployment.yaml
|   |-- frontend-service.yaml
|   |-- frontend-hpa.yaml
|   `-- ingress.yaml
|-- terraform/
|   `-- main.tf
|-- tests/
|   `-- test_api.py
|-- docker-compose.yml
|-- Jenkinsfile
|-- setup.bat
|-- start_backend.bat
|-- start_frontend.bat
|-- sample_bulk_test.csv
`-- README.md
=======
Developer Code
       ↓
GitHub Repository
       ↓
Jenkins CI/CD Pipeline
       ↓
Docker Image Build
       ↓
DockerHub Push
       ↓
Kubernetes Deployment
       ↓
Ingress Routing
       ↓
Auto Scaling using HPA
       ↓
Monitoring using Prometheus & Grafana
       ↓
AWS Infrastructure using Terraform
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b
```

---

<<<<<<< HEAD
- Python 3.11 or newer
- Node.js 18 or newer
- npm

## Setup

### Option 1: Windows setup script

Run this from the project root:

```bat
setup.bat
```

This script installs backend dependencies, trains/regenerates the models, and installs frontend dependencies.

### Option 2: Manual setup

Install backend dependencies:
=======
# Project Structure
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

```bash
FakeGuardAI/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│
├── backend/
│   ├── app/
│   ├── model/
│   ├── requirements.txt
│   ├── Dockerfile
│
├── kubernetes/
│   ├── frontend-deployment.yaml
│   ├── backend-deployment.yaml
│   ├── services.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│
├── terraform/
│   ├── main.tf
│
├── Jenkinsfile
│
└── README.md
```

---

# Machine Learning Workflow

1. Data Collection
2. Data Preprocessing
3. Feature Engineering
4. Model Training
5. Model Evaluation
6. Fake Profile Prediction

## Algorithms Used

* Random Forest
* XGBoost

---

# Docker Setup

## Build Backend Image

```bash
docker build -t fakeguard-backend ./backend
```

## Build Frontend Image

```bash
docker build -t fakeguard-frontend ./frontend
```

---

# Jenkins CI/CD Pipeline

The Jenkins pipeline automates:

* GitHub repository cloning
* Docker image building
* DockerHub image push
* Kubernetes deployment

---

# Kubernetes Deployment

## Start Minikube

```bash
minikube start --driver=docker
```

## Enable Ingress

```bash
minikube addons enable ingress
```

<<<<<<< HEAD
Local URLs:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## Run with Docker Compose

The Docker setup runs the backend and frontend as separate services.

```bash
docker compose up --build
```

Docker URLs:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## Model Training

The training script is:
=======
## Enable Metrics Server

```bash
minikube addons enable metrics-server
```

## Apply Kubernetes Configurations
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

```bash
kubectl apply -f kubernetes/
```

---

<<<<<<< HEAD
- `instagram1/Instagram_fake_profile_dataset.csv`
- `instagram2/train.csv`
- `instagram2/test.csv`
- `twitter1/bot_detection_data.csv`
- `twitter2/twitter_human_bots_dataset.csv`

The generated artifacts are saved in `backend/models/`:
=======
# Auto Scaling

Horizontal Pod Autoscaler (HPA) automatically scales pods based on CPU utilization.
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

## Configuration

<<<<<<< HEAD
The backend expects these files to exist before startup.
=======
* Minimum Replicas: 2
* Maximum Replicas: 5
* CPU Threshold: 70%
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

---

<<<<<<< HEAD
| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Health check and model summary |
| `POST` | `/predict` | Predict one Instagram or Twitter/X profile |
| `POST` | `/predict/bulk?platform=instagram` | Upload a CSV and scan many profiles |
| `GET` | `/history` | Read saved prediction history |
| `GET` | `/dashboard` | Read aggregate dashboard statistics |
| `GET` | `/model-info` | Read model metadata and metrics |
| `GET` | `/metrics` | Prometheus-style metrics |
| `DELETE` | `/history/clear` | Clear local prediction history |
=======
# Monitoring
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

## Prometheus

Used for collecting Kubernetes cluster metrics.

## Grafana

Used for visualizing:

* CPU usage
* Memory usage
* Pod health
* Cluster performance

---

# Terraform AWS Infrastructure

Terraform automates:

<<<<<<< HEAD
Use the frontend Bulk Check tab or call the API directly:

```bash
curl -X POST "http://localhost:8000/predict/bulk?platform=instagram" ^
  -F "file=@sample_bulk_test.csv"
=======
* EC2 instance creation
* Security group setup
* Infrastructure provisioning

## Terraform Commands

```bash
terraform init
terraform plan
terraform apply
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b
```

---

<<<<<<< HEAD
- `username`
- `profile pic`
- `nums/length username`
- `fullname words`
- `nums/length fullname`
- `name==username`
- `description length`
- `external URL`
- `private`
- `#posts`
- `#followers`
- `#follows`

For Twitter/X CSVs, useful columns include:

- `username`
- `Retweet Count`
- `Mention Count`
- `Follower Count`
- `Verified`

Sample files are available in `data/`.

## Testing

Run the API test suite from the project root:
=======
# Kubernetes Verification Commands
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

```bash
kubectl get pods
kubectl get svc
kubectl get ingress
kubectl get hpa
```

---

<<<<<<< HEAD
## Kubernetes

The `kubernetes/` folder contains manifests for:

- Backend deployment, service, and HPA
- Frontend deployment, service, and HPA
- Ingress configuration

Apply them with `kubectl` after updating image names and namespaces to match your environment.

## Jenkins and Terraform

- `Jenkinsfile` defines a pipeline that builds and pushes the backend and frontend Docker images.
- `terraform/main.tf` provisions a basic AWS EC2 instance and security group for DevOps-related deployment work.

## Notes

- Prediction history is stored locally in `backend/predictions.db`.
- The frontend calls the backend at `http://localhost:8000`.
- Generated datasets, model artifacts, `node_modules`, caches, and local environment files should stay out of Git.
- The repo contains an older `backend/model/` directory from an earlier single-model version, but the current API loads artifacts from `backend/models/`.
- This project is intended for learning and demonstration. Real-world fake profile detection should use stronger datasets, continuous validation, abuse monitoring, and careful privacy/security review.
=======
# Advantages of the Project

* Scalable cloud-native architecture
* Automated deployment pipeline
* Real-time monitoring
* Containerized application deployment
* Infrastructure automation
* High availability using Kubernetes
* CI/CD integration
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b

---

# Future Enhancements

* Deep Learning integration
* Real-time social media API analysis
* Multi-platform profile verification
* Advanced fraud analytics dashboard
* Authentication and user management

---

# Conclusion

FakeGuard AI combines:

* Machine Learning
* Full Stack Development
* DevOps
* Cloud Infrastructure
* Kubernetes orchestration

to create a scalable and production-ready fake profile detection platform.

---

# Author

**Seshaveni Veeramreddy**

Seshaveni

<<<<<<< HEAD
## License

This project is for educational purposes.
=======
>>>>>>> 854b9fa327a9f54c6dba7d8483c2a24307089c8b
