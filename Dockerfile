# Usamos la imagen oficial de Python 3.10 slim para mantener un tamaño ligero
FROM python:3.10-slim

# Evitamos que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evitamos que Python haga buffer de stdout y stderr
ENV PYTHONUNBUFFERED=1

# Instalamos Poetry
RUN pip install poetry==1.7.1

# Configuramos Poetry para no crear entornos virtuales dentro del contenedor
RUN poetry config virtualenvs.create false

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos solo los archivos de dependencias primero (para aprovechar el caché de capas de Docker)
COPY pyproject.toml /app/

# Instalamos las dependencias del proyecto
RUN poetry install --no-dev --no-interaction --no-ansi

# Copiamos el resto del código del proyecto
COPY . /app/

# Exponemos el puerto que usa Streamlit
EXPOSE 8501

# Definimos variables de entorno por defecto
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Creamos un usuario no-root por seguridad
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Comando por defecto para ejecutar el dashboard
CMD ["python", "run_pipeline.py", "dashboard"]
