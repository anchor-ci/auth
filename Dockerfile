FROM python:3.7-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "/app/application.py"]
