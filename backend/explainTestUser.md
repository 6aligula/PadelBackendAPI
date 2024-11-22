### **Informe Expandido sobre la Implementación y Ejecución de Pruebas Unitarias**

Este documento presenta un análisis detallado de la implementación de pruebas unitarias para los módulos de usuarios y reservaciones de una API basada en Django Rest Framework (DRF). También incluye el proceso de ejecución dentro de un contenedor Docker, la generación de reportes de cobertura y un análisis exhaustivo de los resultados obtenidos.

---

## **1. Introducción**

Las pruebas unitarias son una herramienta clave en el desarrollo de software. Verifican el correcto funcionamiento de componentes específicos en aislamiento, asegurando:
- **Calidad del Código**: Detectan errores antes de desplegar el sistema.
- **Estabilidad**: Previenen la aparición de problemas durante cambios o mejoras.
- **Documentación del Comportamiento**: Reflejan cómo deben operar las unidades probadas.

En este proyecto, las pruebas cubren:
1. **Módulo de Usuarios**:
   - Registro, inicio de sesión, actualización de perfil, permisos y eliminación.
2. **Módulo de Reservaciones**:
   - Creación de reservas, manejo de duplicidad y validaciones relacionadas con las instalaciones.
3. **Serializadores**:
   - Verificación de los datos serializados y validaciones personalizadas.
4. **Modelos**:
   - Pruebas de propiedades y comportamientos definidos en los modelos de Django.

---

## **2. Configuración del Entorno**

### **2.1. Contenedor Docker**
Se configuró un entorno Docker para simplificar el desarrollo y la ejecución de pruebas. El servicio incluye:
- Django como API.
- MySQL como base de datos.

**Archivo `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  web:
    build: .
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
    depends_on:
      - db

  db:
    image: mysql:8
    environment:
      MYSQL_DATABASE: test_db
      MYSQL_USER: admin
      MYSQL_PASSWORD: adminpassword
      MYSQL_ROOT_PASSWORD: rootpassword
```

### **2.2. Acceso al Contenedor**
1. Inicia los servicios:
   ```bash
   docker-compose up -d
   ```
2. Lista los contenedores activos:
   ```bash
   docker ps
   ```
3. Accede al contenedor que ejecuta Django:
   ```bash
   docker exec -it <container_id> bash
   ```

---

## **3. Ejecución de Pruebas**

### **3.1. Ejecución Manual de Pruebas**
En el contenedor, navega al directorio del proyecto y ejecuta las pruebas:
```bash
python manage.py test backend.test_user_views
python manage.py test backend.test_reservation_views
python manage.py test backend.test_serializers
python manage.py test backend.test_models
```

### **3.2. Generación de Reportes de Cobertura**
1. Instala `coverage`:
   ```bash
   pip install coverage
   ```
2. Ejecuta todas las pruebas y genera un reporte:
   ```bash
   coverage run --source='backend' manage.py test backend
   coverage report -m
   ```
3. Genera un reporte en HTML:
   ```bash
   coverage html
   ```
   Abre `htmlcov/index.html` en tu navegador para una visualización detallada.

---

## **4. Análisis de Resultados**

### **4.1. Resumen de Logs**
#### Ejecución Total:
```plaintext
Ran 31 tests in 27.478s
OK
```
- **Número Total de Pruebas:** 31
- **Estado:** Todas las pruebas pasaron exitosamente.

#### Cobertura:
```plaintext
TOTAL                                  447     12    97%
```
- **Cobertura General:** 97%
- **Archivos con Cobertura Incompleta:**
  - `serializers.py`: 98% (una línea de validación no cubierta).
  - `reservation_views.py`: 96% (caso límite no probado).
  - `user_views.py`: 90% (validaciones adicionales no testeadas).

---

### **4.2. Casos Probados**

#### **Usuarios:**
- **Registro**:
  - Verifica que todos los campos obligatorios sean proporcionados.
  - Manejo de campos opcionales vacíos.
  - Evita duplicidad de nombres de usuario.
- **Inicio de Sesión**:
  - Generación de tokens de autenticación.
- **Actualización de Perfil**:
  - Restricciones para usuarios no autenticados.
  - Validación de permisos administrativos.
- **Eliminación**:
  - Solo usuarios con permisos administrativos pueden eliminar cuentas.

#### **Reservaciones:**
- **Creación**:
  - Manejo de duplicidad en fecha e instalación.
  - Validación de datos relacionados con instalaciones inexistentes.
- **Obtención**:
  - Acceso restringido a usuarios autenticados.
  - Manejo de escenarios con datos inválidos.

#### **Serializadores:**
- Validación de datos en `UserSerializer` y `ReservationSerializer`.
- Verificación de restricciones personalizadas en reservas.

#### **Modelos:**
- Validación de relaciones entre modelos.
- Restricciones de unicidad para reservas.

---

## **5. Beneficios del Enfoque Aplicado**

1. **Aseguramiento de Calidad**:
   - Validaciones específicas para garantizar que los datos sean precisos antes de ingresar a la base de datos.

2. **Identificación Temprana de Errores**:
   - Detectar problemas en lógica de negocio antes de despliegues.

3. **Cobertura Exhaustiva**:
   - Pruebas tanto para vistas como para modelos y serializadores, asegurando un enfoque integral.

4. **Facilidad de Mantenimiento**:
   - Las pruebas actúan como documentación funcional, simplificando futuros cambios en el sistema.

5. **Escalabilidad**:
   - Un marco sólido para agregar nuevos módulos sin comprometer la estabilidad.

---

## **6. Conclusión**

Este proyecto implementa pruebas unitarias y reportes de cobertura como prácticas estándar de desarrollo. Con una cobertura del 97%, se ha demostrado que el sistema es robusto y preparado para manejar escenarios reales. Sin embargo, se recomienda:
- Completar el 100% de cobertura, especialmente en `user_views` y `serializers`.
- Documentar explícitamente casos límite para futuras mejoras.

Con este enfoque, el proyecto está listo para ser mantenido y escalado eficientemente.