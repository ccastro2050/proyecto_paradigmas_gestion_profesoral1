# API Gestión Profesoral — FastAPI (puerto 8029)
FROM python:3.12-slim

WORKDIR /app

# Primero las dependencias y después el código: mientras requirements.txt no
# cambie, Docker reutiliza la capa del pip install y reconstruir es rápido.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8029

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8029"]
