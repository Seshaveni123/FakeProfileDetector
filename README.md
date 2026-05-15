# FakeGuard AI — Cloud-Native Fake Profile Detection Web App

## Overview

FakeGuard AI is an AI-powered fake profile detection web application designed to classify social media profiles as **Fake** or **Genuine** using Machine Learning models like **Random Forest** and **XGBoost**.

The project integrates **Machine Learning, Full Stack Development, DevOps, Cloud Computing, and Kubernetes orchestration** to build a scalable and production-ready application.

---

# Features

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
```

---

# Project Structure

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

## Enable Metrics Server

```bash
minikube addons enable metrics-server
```

## Apply Kubernetes Configurations

```bash
kubectl apply -f kubernetes/
```

---

# Auto Scaling

Horizontal Pod Autoscaler (HPA) automatically scales pods based on CPU utilization.

## Configuration

* Minimum Replicas: 2
* Maximum Replicas: 5
* CPU Threshold: 70%

---

# Monitoring

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

* EC2 instance creation
* Security group setup
* Infrastructure provisioning

## Terraform Commands

```bash
terraform init
terraform plan
terraform apply
```

---

# Kubernetes Verification Commands

```bash
kubectl get pods
kubectl get svc
kubectl get ingress
kubectl get hpa
```

---

# Advantages of the Project

* Scalable cloud-native architecture
* Automated deployment pipeline
* Real-time monitoring
* Containerized application deployment
* Infrastructure automation
* High availability using Kubernetes
* CI/CD integration

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


