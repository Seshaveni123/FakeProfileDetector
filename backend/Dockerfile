FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import sys, urllib.request; response = urllib.request.urlopen('http://127.0.0.1:8000/', timeout=3); sys.exit(0 if 200 <= response.status < 400 else 1)"]

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
