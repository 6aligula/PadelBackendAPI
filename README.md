# Backend Django

Este es el backend de Django de la aplicación, contenerizado para asegurar un entorno de ejecución consistente.

## Dockerización

El backend de Django está configurado para ejecutarse en un contenedor Docker, lo que simplifica el despliegue y la gestión de dependencias.

### Dockerfile

El `Dockerfile` utiliza la imagen de Python 3.8 y prepara el entorno de Django.

```dockerfile
FROM python:3.8
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
EXPOSE 8000
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]

```


### Docker Compose
El archivo `docker-compose.yml` establece el servicio, los volúmenes, los puertos y la red.

```dockerfile
version: '3.8'

services:
  frontend:
    build: .
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - CHOKIDAR_USEPOLLING=true
    networks:
      - app-network

networks:
  app-network:
    external: true
```
### Uso
Para iniciar el backend:

```bash
docker-compose up --build
```

La red app-network conecta el backend con otros servicios, como el frontend. Asegúrese de que la red esté definida como se describe en el archivo docker-compose.yml.
