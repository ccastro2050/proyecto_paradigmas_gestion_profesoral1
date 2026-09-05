# Dockerfile del FRONT — Flask + Jinja2, puerto 8027.
#
# LA API DE ESTE MÓDULO TAMBIÉN ESTÁ EN PYTHON, y eso hace que la separación
# entre los dos procesos haya que sostenerla a pulso: nada impide, salvo la
# disciplina, importar el código de la API desde aquí. Por eso el front vive
# en su propia imagen, con sus propias dependencias —Flask y requests, ni
# FastAPI ni el driver de PostgreSQL— y lo único que comparten es el JSON.
#
# Fíjese en lo que este archivo NO instala: `asyncpg`. La ausencia no es un
# olvido, es la comprobación. Este proceso no puede llegar a la base de datos
# ni queriendo.
FROM python:3.12-slim

WORKDIR /app

# Primero las dependencias y después el código: mientras requirements.txt no
# cambie, Docker reutiliza la capa del pip install.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PUERTO=8027
EXPOSE 8027

CMD ["python", "app.py"]
