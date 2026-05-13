# 🛡️ Platform-Aware Fake Profile Detection System

> **ML-powered fake profile detection for Instagram & Twitter with full DevOps & Cloud Integration**

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/FakeProfileDetector/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/FakeProfileDetector/actions)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [DevOps & Cloud](#-devops--cloud-integration)
- [Deployment](#-deployment)
- [Screenshots](#-screenshots)

---

## 🎯 Overview

This project is a **full-stack, end-to-end fake profile detection system** that uses separate Machine Learning models for **Instagram** and **Twitter** platforms. It features:

- **Platform-specific ML models** (Random Forest + XGBoost)
- **FastAPI REST API** with Prometheus metrics
- **React frontend** with platform-aware dynamic forms
- **Docker containerization** with docker-compose
- **CI/CD pipeline** via GitHub Actions
- **Infrastructure as Code** with Terraform
- **Monitoring & Observability** with Prometheus + Grafana
- **Database storage** with SQLite (local) / Supabase (cloud)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│                    React Frontend (Vite)                     │
│              Platform Selector → Dynamic Forms              │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Instagram    │  │ Twitter      │  │ Prometheus       │  │
│  │ Model (.pkl) │  │ Model (.pkl) │  │ /metrics         │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SQLite / Supabase (PostgreSQL)           │  │
│  │              Prediction History Storage               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│   Monitoring: Prometheus (scrape) → Grafana (visualize)     │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Machine Learning
- ✅ Separate models per platform (Instagram / Twitter)
- ✅ Random Forest (primary) + XGBoost (optional)
- ✅ Feature engineering: `follower_ratio`, `engagement_rate`, `activity_score`
- ✅ Explainable AI — human-readable prediction explanations
- ✅ Feature importance visualization

### Backend (FastAPI)
- ✅ `GET /` → Health check
- ✅ `POST /predict` → Platform-aware prediction
- ✅ `POST /predict/bulk` → CSV bulk upload
- ✅ `GET /history` → Prediction history (filterable by platform)
- ✅ `GET /dashboard` → Analytics with platform breakdown
- ✅ `GET /model-info` → Model performance metrics
- ✅ `GET /metrics` → Prometheus metrics endpoint
- ✅ Pydantic validation & CORS support

### Frontend (React + Vite)
- ✅ Platform selector (Instagram / Twitter)
- ✅ Dynamic input forms per platform
- ✅ Real/Fake demo data loaders
- ✅ Confidence gauge & risk level visualization
- ✅ Feature importance bar charts
- ✅ Bulk CSV upload
- ✅ Analytics dashboard with platform breakdown
- ✅ Prediction history table
- ✅ Toast notifications & loading spinners
- ✅ Premium glassmorphism dark theme

### DevOps & Cloud
- ✅ Docker multi-stage builds
- ✅ Docker Compose (backend + frontend + Prometheus + Grafana)
- ✅ GitHub Actions CI/CD pipeline
- ✅ Terraform IaC for AWS EC2
- ✅ Prometheus metrics collection
- ✅ Grafana dashboard provisioning
- ✅ Supabase PostgreSQL schema

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **ML** | scikit-learn, XGBoost, pandas, NumPy |
| **Backend** | FastAPI, Pydantic, Uvicorn |
| **Frontend** | React 18, Vite, CSS (glassmorphism) |
| **Database** | SQLite (local), Supabase PostgreSQL (cloud) |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **IaC** | Terraform (AWS) |
| **Monitoring** | Prometheus, Grafana |
| **Version Control** | Git, GitHub |

---

## 📁 Project Structure

```
FakeProfileDetector/
├── ml/                          # Machine Learning
│   ├── generate_dataset.py      # Synthetic dataset generator
│   └── train_models.py          # Model training pipeline
├── backend/                     # FastAPI Backend
│   ├── app.py                   # API endpoints
│   └── requirements.txt         # Python dependencies
├── frontend/                    # React Frontend
│   ├── src/
│   │   ├── App.jsx              # Main application
│   │   ├── index.css            # Design system
│   │   └── main.jsx             # Entry point
│   ├── package.json
│   └── vite.config.js
├── data/                        # Generated datasets
│   ├── instagram_dataset.csv
│   ├── twitter_dataset.csv
│   ├── sample_instagram_bulk.csv
│   └── sample_twitter_bulk.csv
├── models/                      # Trained models
│   ├── insta_model.pkl
│   ├── insta_scaler.pkl
│   ├── insta_metadata.json
│   ├── twitter_model.pkl
│   ├── twitter_scaler.pkl
│   └── twitter_metadata.json
├── docker/                      # Docker configs
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── monitoring/                  # Observability
│   ├── prometheus.yml
│   └── grafana-datasources.yml
├── terraform/                   # Infrastructure as Code
│   └── main.tf
├── database/                    # DB Schema
│   └── schema.sql
├── tests/                       # API Tests
│   └── test_api.py
├── .github/workflows/           # CI/CD
│   └── ci-cd.yml
├── docker-compose.yml           # Full stack compose
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional, for containerized deployment)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/FakeProfileDetector.git
cd FakeProfileDetector
```

### 2. Generate Datasets & Train Models
```bash
pip install -r backend/requirements.txt
python ml/generate_dataset.py
python ml/train_models.py
```

### 3. Start the Backend
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
API available at: http://localhost:8000

### 4. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
UI available at: http://localhost:5173

### 5. (Optional) Run with Docker Compose
```bash
docker-compose up -d --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/fakeguard123)

---

## 📡 API Documentation

### `POST /predict`

Predict if a profile is fake or real.

**Request (Instagram):**
```json
{
  "platform": "instagram",
  "username": "test_user",
  "followers_count": 4500,
  "following_count": 380,
  "posts_count": 340,
  "account_age_days": 1800,
  "bio_length": 90,
  "has_profile_pic": 1,
  "avg_likes": 180,
  "avg_comments": 12
}
```

**Request (Twitter):**
```json
{
  "platform": "twitter",
  "username": "test_tweeter",
  "followers_count": 3200,
  "following_count": 450,
  "tweets_count": 8500,
  "account_age_days": 2900,
  "bio_length": 110,
  "has_profile_pic": 1,
  "listed_count": 45,
  "avg_retweets": 8,
  "avg_favorites": 25,
  "reply_ratio": 0.25
}
```

**Response:**
```json
{
  "platform": "instagram",
  "is_fake": 0,
  "probability": 0.0523,
  "label": "Real Profile",
  "risk_level": "low",
  "feature_importance": { ... },
  "explanation": [
    "✅ Has a profile picture",
    "📅 Well-established account (over a year old)"
  ]
}
```

### Other Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/predict/bulk?platform=instagram` | Bulk CSV prediction |
| `GET` | `/history?platform=twitter` | Prediction history |
| `GET` | `/dashboard` | Analytics dashboard |
| `GET` | `/model-info` | Model information |
| `GET` | `/metrics` | Prometheus metrics |
| `DELETE` | `/history/clear` | Clear history |

---

## ☁️ DevOps & Cloud Integration

### Version Control
- Git repository with `main` and `dev` branches
- `.gitignore` configured for Python, Node, Terraform, Docker

### Containerization (Docker)
```bash
# Build and run full stack
docker-compose up -d --build

# View logs
docker-compose logs -f backend
```

### CI/CD Pipeline (GitHub Actions)
The pipeline runs on push to `main`/`dev`:
1. **Backend Tests** — Install deps, generate data, train models, run pytest
2. **Frontend Build** — npm ci, build production bundle
3. **Docker Build** — Build backend + frontend images
4. **Deploy** — Production deployment (main branch only)

### Infrastructure as Code (Terraform)
```bash
cd terraform
terraform init
terraform plan
terraform apply
```
Provisions: AWS EC2 + Security Groups + Docker auto-setup

### Monitoring & Observability
- **Prometheus** scrapes `GET /metrics` every 15s
- **Grafana** pre-configured with Prometheus datasource
- Metrics tracked: predictions_total, predictions_fake/real, per-platform counts, request duration

### Security (DevSecOps)
- CORS configured on backend
- Pydantic input validation on all endpoints
- Security headers via nginx
- Supabase Row Level Security (RLS)
- No hardcoded secrets (environment variables)

---

## 🚀 Deployment

### Option A: AWS EC2 (Terraform)
```bash
cd terraform && terraform apply
# SSH into instance, docker-compose up
```

### Option B: Render (Backend)
1. Connect GitHub repo to Render
2. Set build command: `pip install -r backend/requirements.txt && python ml/generate_dataset.py && python ml/train_models.py`
3. Set start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

### Option C: Vercel (Frontend)
1. Connect GitHub repo to Vercel
2. Set root directory: `frontend`
3. Framework: Vite
4. Build command: `npm run build`

### Option D: Supabase (Database)
1. Create Supabase project
2. Run `database/schema.sql` in SQL Editor
3. Update backend to use Supabase connection string

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
python -m pytest tests/ -v
```

---

## 📊 Model Performance

| Platform | Model | Accuracy | Precision | Recall | F1 Score | AUC-ROC |
|----------|-------|----------|-----------|--------|----------|---------|
| Instagram | Random Forest | ~97% | ~96% | ~97% | ~97% | ~99% |
| Twitter | Random Forest | ~97% | ~96% | ~97% | ~97% | ~99% |

---

## 👨‍💻 Author

**Seshaveni** — B.Tech CSE

---

## 📄 License

This project is for educational purposes.
