#!/bin/bash

echo "Construyendo la imagen de Docker..."
docker build -t sistema-notas .

echo "Otorgando permisos al servidor gráfico (X11)..."
xhost +local:docker

echo "Ejecutando el contenedor..."
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro sistema-notas
