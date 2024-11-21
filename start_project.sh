#!/bin/bash

# Obtiene la dirección IP del host (ajusta este comando según tu sistema operativo y configuración de red)
HOST_IP=$(hostname -I | awk '{print $1}')
echo $HOST_IP


# Exporta la IP del host y 'localhost' como valores para DJANGO_ALLOWED_HOSTS
export DJANGO_ALLOWED_HOSTS=$HOST_IP,localhost

# Lanza los contenedores y construye si es necesario
docker-compose up --build
