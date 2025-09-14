# Imagen base oficial de Python
FROM python:3.13-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los ficheros de dependencias
COPY requirements.txt .

# Instalamos dependencias
RUN pip install -r requirements.txt

# Copiamos todo el proyecto
COPY . .

# Entramos a la carpeta donde esta el archivo app.py
WORKDIR /app/backend

# Puerto donde se debe ejecutar
EXPOSE 5000

# Comando para accionar el contenedor
CMD ["python", "app.py"]
