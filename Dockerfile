FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mock_salon_backend.py landing.html Retell* .env.example ./
COPY static ./static
EXPOSE 8007
CMD ["uvicorn", "mock_salon_backend:app", "--host", "0.0.0.0", "--port", "8007"]
