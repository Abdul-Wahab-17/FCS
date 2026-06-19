FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn python-multipart pydantic numpy opencv-python-headless

COPY src ./src
COPY .env.example .env.example

EXPOSE 8000

CMD ["python", "src/main.py"]
