FROM python:3.12-slim

# No generar .pyc y mostrar los logs al momento
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

# Primero las dependencias, para que Docker reutilice esta capa si solo cambia el código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código fuente de la API
COPY src/ .

# Usuario sin privilegios, dueño del código, para no ejecutar la app como root
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "main.py"]
