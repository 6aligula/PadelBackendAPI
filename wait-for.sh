#!/bin/bash

# Uso: wait-for.sh host:puerto -- comando
HOST=$(echo $1 | cut -d: -f1)
PORT=$(echo $1 | cut -d: -f2)
shift
CMD="$@"

until nc -z "$HOST" "$PORT"; do
  >&2 echo "El servicio $HOST:$PORT no está disponible aún - esperando..."
  sleep 1
done

>&2 echo "El servicio $HOST:$PORT está disponible - ejecutando comando"
exec $CMD
