# Usar imagen base oficial de Python
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente (models, services y main.py)
COPY models/ ./models/
COPY services/ ./services/
COPY main.py .

# Cambiar permisos
RUN chmod -R 755 /app

# Comando de inicio
CMD ["python", "main.py"]
