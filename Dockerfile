# Usamos una imagen base oficial de Python ligera
FROM python:3.11-slim

# Evitamos que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Forzamos a que la salida de Python no use buffer, ideal para ver logs en tiempo real
ENV PYTHONUNBUFFERED=1

# Instalamos las dependencias del sistema necesarias para interfaces gráficas (Tkinter/X11)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxft2 \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero los requerimientos para aprovechar el caché de capas de Docker
COPY requirements.txt /app/

# Instalamos las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el resto del código del proyecto al directorio de trabajo
COPY . /app/

# Comando por defecto para ejecutar la aplicación
CMD ["python", "main.py"]
