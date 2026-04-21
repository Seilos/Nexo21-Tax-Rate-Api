# Usa una imagen oficial de Python de tamaño reducido
FROM python:3.11-slim

# Instala dependencias del sistema necesarias para compilar paquetes (ej. psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo los requerimientos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del microservicio
COPY . .

# Expone el puerto que usa Koyeb/Docker por defecto (usualmente 8000)
EXPOSE 8000

# Variables de entorno por defecto para producción
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV RUN_MAIN=true

# Comando que se ejecutará al iniciar el contenedor
# Ejecuta las migraciones, recoge los estáticos e inicia Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn core.wsgi:application --bind 0.000.0:8000"]
