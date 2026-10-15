FROM python:3.11-slim
WORKDIR /app
COPY services/history-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/history-service/app.py .
EXPOSE 8001
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/', timeout=3)"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
