# ---------------------------------------------------------------------------
# Cyber Sentinel — Security Analytics Dashboard
# Imagen Docker reproducible (Python 3.11 + Streamlit)
# ---------------------------------------------------------------------------
FROM python:3.11-slim

LABEL maintainer="Cyber Sentinel — Proyecto académico"
LABEL description="Dashboard interactivo de analítica de eventos de ciberseguridad (uso educativo)"

WORKDIR /app

# Dependencias del sistema mínimas (sin bases de datos ni servicios externos)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python primero (mejor cacheo de capas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto (incluye data/cybersecurity_attacks.csv)
COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--browser.gatherUsageStats=false"]
