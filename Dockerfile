FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/*.py /app/
COPY src/controllers/* /app/controllers/
COPY src/managers/* /app/managers/

ENV PYTHONUNBUFFERED=1
CMD [ "gunicorn", "application", "--bind=0.0.0.0:8000" ]
