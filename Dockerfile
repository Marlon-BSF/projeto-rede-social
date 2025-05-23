# Dockerfile para servidor Python
FROM python:3.10-slim

WORKDIR /app

COPY servidor.py ./

CMD ["python3", "servidor.py", "S1", "8000", "log_servidor_S1.txt"]
