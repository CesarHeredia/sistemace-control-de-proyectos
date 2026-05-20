# Instrucciones para Docker

Este proyecto utiliza una interfaz gráfica (GUI) con `customtkinter`, por lo que para ejecutarlo en Docker dentro de Linux se requieren un par de configuraciones para conectar la interfaz del contenedor con la pantalla de tu ordenador.

## Opción 1: Usar el script automatizado (Recomendado)

He creado un archivo llamado `run_docker.sh` que hace todo el proceso por ti.
Para utilizarlo, primero dale permisos de ejecución en tu terminal:

```bash
chmod +x run_docker.sh
```

Luego, simplemente ejecútalo:

```bash
./run_docker.sh
```

---

## Opción 2: Ejecutar los comandos manualmente paso a paso

Si prefieres hacerlo tú mismo en la terminal, sigue estos 3 pasos:

**1. Construye la imagen de Docker**
Esto descargará Python, las dependencias del sistema y las librerías de tu archivo `requirements.txt`.
```bash
docker build -t sistema-notas .
```

**2. Otorga permisos al servidor gráfico**
El contenedor necesita permisos para poder abrir una ventana en tu pantalla.
```bash
xhost +local:docker
```

**3. Ejecuta el contenedor**
Lo que hace es compartir la pantalla actual (`$DISPLAY`) y los recursos gráficos con el contenedor para que puedas visualizar la ventana interactiva:
```bash
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:ro sistema-notas
```
