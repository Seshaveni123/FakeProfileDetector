# FakeGuard AI - Fake Profile Detector

FakeGuard AI is a full-stack machine learning project for detecting fake social media profiles on Instagram and Twitter/X.
It includes a FastAPI backend, a React + Vite frontend, separate trained models for each platform, SQLite-based prediction
history, bulk CSV scanning, dashboard analytics, and model metadata views.

## Features

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

## Tech Stack

| Area | Tools |
| --- | --- |
| Backend | FastAPI, Uvicorn, Pydantic |
| Machine Learning | scikit-learn, XGBoost, pandas, NumPy |
| Frontend | React 18, Vite, CSS |
| Database | SQLite |
| Testing | pytest, FastAPI TestClient |
| DevOps | Docker, Docker Compose, Kubernetes, Jenkins, Terraform |

## Project Structure

```text
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
```

## Prerequisites

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

```bash
pip install -r backend/requirements.txt
```

Train or regenerate the ML models:

```bash
python ml/train_models.py
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

## Run the Application

Start the backend:

```bat
start_backend.bat
```

Or manually:

```bash
cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend in a second terminal:

```bat
start_frontend.bat
```

Or manually:

```bash
cd frontend
npm run dev
```

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

```bash
python ml/train_models.py
```

It loads the local datasets from:

- `instagram1/Instagram_fake_profile_dataset.csv`
- `instagram2/train.csv`
- `instagram2/test.csv`
- `twitter1/bot_detection_data.csv`
- `twitter2/twitter_human_bots_dataset.csv`

The generated artifacts are saved in `backend/models/`:

- `insta_model.pkl`
- `insta_scaler.pkl`
- `insta_metadata.json`
- `twitter_model.pkl`
- `twitter_scaler.pkl`
- `twitter_metadata.json`

The backend expects these files to exist before startup.

## API Endpoints

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

## Example Requests

Instagram prediction:

```json
{
  "platform": "instagram",
  "username": "sample_user",
  "profile_pic": 1,
  "nums_length_username": 0.0,
  "fullname_words": 2,
  "nums_length_fullname": 0.0,
  "name_eq_username": 0,
  "description_length": 80,
  "external_url": 1,
  "private": 0,
  "posts_count": 120,
  "followers_count": 1500,
  "following_count": 350
}
```

Twitter/X prediction:

```json
{
  "platform": "twitter",
  "username": "sample_twitter_user",
  "retweet_count": 8,
  "mention_count": 2,
  "follower_count_twitter": 3200,
  "verified": 0
}
```

Typical response:

```json
{
  "platform": "instagram",
  "is_fake": 0,
  "probability": 0.0523,
  "label": "Real Profile",
  "risk_level": "low",
  "feature_importance": {
    "Followers": 0.34
  },
  "explanation": [
    "Has a profile picture",
    "Detailed bio/description present"
  ]
}
```

## Bulk CSV Upload

Use the frontend Bulk Check tab or call the API directly:

```bash
curl -X POST "http://localhost:8000/predict/bulk?platform=instagram" ^
  -F "file=@sample_bulk_test.csv"
```

For Instagram CSVs, useful columns include:

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

```bash
python -m pytest tests/ -v
```

The tests import the FastAPI app directly, so the trained model files in `backend/models/` must be available.

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

## Author

Seshaveni

## License

This project is for educational purposes.
