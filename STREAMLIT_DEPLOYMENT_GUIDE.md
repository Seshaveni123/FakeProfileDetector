# 🚀 FakeGuard AI — Streamlit Deployment & User Guide

This guide explains how to run and deploy the **FakeGuard AI Fake Profile Detection Platform** using Streamlit locally and in the cloud (Streamlit Community Cloud, Hugging Face Spaces, Docker, AWS, Render).

---

## 🌟 Key Features of the Streamlit App

1. **🎯 Multi-Platform Profile Scanner**:
   - Platform selector: **Instagram** (11 features) and **Twitter / X** (4 features).
   - Instant quick presets: **Genuine User**, **Suspicious Account**, **Fake / Bot Account**.
   - Live **Risk Probability Gauge** with color-coded risk zones (Critical, High, Medium, Low).
   - **Explainable AI (XAI)** reasoning cards detailing why the profile was flagged.
   - Dynamic **Feature Importance Chart** powered by Plotly.

2. **📁 High-Throughput Bulk CSV Batch Scanner**:
   - Drag-and-drop CSV file upload.
   - Built-in **Demo Dataset loader** (10 pre-configured profiles).
   - Batch progress bar and summary metric cards (Total Scans, Fake %, Genuine %, Average Risk Score).
   - Risk distribution donut chart.
   - **1-click CSV export** of results.

3. **📊 Real-Time Threat Intelligence Dashboard**:
   - Global metrics: Total scans, Fake detection rate, Genuine count, Average risk.
   - Platform breakdown bar charts (Instagram vs Twitter).
   - Threat risk tier distribution pie chart.
   - Live stream of recent detections with timestamps.

4. **📜 SQLite Audit Log**:
   - Full persistence in `predictions.db`.
   - Filter by Platform and Risk Level.
   - 1-click **Export Filtered Audit History as CSV**.
   - Database cleanup option.

5. **🧠 ML Architecture & Metrics Deep-Dive**:
   - Algorithm comparison: **XGBoost** vs **Random Forest**.
   - Benchmarks: Accuracy, Precision, Recall, F1 Score, ROC-AUC.
   - Dataset schema & feature dictionary.

---

## 💻 1. Running Locally (Windows, Mac, Linux)

### Step 1: Install Dependencies
```bash
pip install -r requirements_streamlit.txt
```

### Step 2: Launch the App
Run the following command:
```bash
streamlit run streamlit_app.py
```
Or simply double-click **`start_streamlit.bat`** on Windows.

The app will open automatically in your browser at:
`http://localhost:8501`

---

## ☁️ 2. Deploying on Streamlit Community Cloud (Free & 1-Click)

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Add FakeGuard AI Streamlit App"
   git push origin main
   ```
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with your GitHub account.
3. Click **"New App"**.
4. Select your repository: `Seshaveni123/FakeProfileDetector` (or your fork).
5. Set:
   - **Main file path**: `streamlit_app.py`
   - **Python version**: `3.10` or `3.11`
6. Click **Deploy!** 🚀

---

## 🐳 3. Running with Docker

You can build and run a containerized Streamlit instance:

```bash
# Build Docker image
docker build -f Dockerfile.streamlit -t fakeguard-streamlit .

# Run Docker container
docker run -p 8501:8501 fakeguard-streamlit
```

Access at `http://localhost:8501`.

---

## 🧪 4. Running the Backend Tests

To verify backend ML models and API endpoints:
```bash
python -c "
import sys, os
sys.path.insert(0, 'backend')
sys.path.insert(0, 'tests')
import test_api
test_api.test_health_check()
test_api.test_predict_instagram_real()
test_api.test_predict_instagram_fake()
test_api.test_predict_twitter_real()
test_api.test_predict_twitter_fake()
test_api.test_model_info()
test_api.test_dashboard_empty()
test_api.test_history()
test_api.test_metrics_endpoint()
print('All backend test suites passed 100%!')
"
```
