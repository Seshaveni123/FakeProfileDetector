FROM python:3.11-slim
WORKDIR /app
COPY services/prediction-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/prediction-service/app.py .
COPY backend/models ./models
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=3)"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
