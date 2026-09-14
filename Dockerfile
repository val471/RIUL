#Imagen de base
From Python:3.12-slim

# variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1

#Logs
ENV PYTHONNUNBUFFERED=1

#Directorio de trabajo

WORKDIR /app

#Dependencias del sistema

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

#Dependecias de Python
COPY requirements.txt .

#instalamos la dependencia 

RUN pip install --no-cache-dir -r requirements.txt

#Codigo de la aplicación
COPY . .

#Puerto 

EXPOSE 5000

#Gunicorn exect app en flask
CMD [ "Gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app" ]