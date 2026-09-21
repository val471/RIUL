#Imagen de base
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Dependencias de Python
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Código de la aplicación
COPY . .

# Puerto
EXPOSE 5000

# Gunicorn ejecuta la aplicación Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]
