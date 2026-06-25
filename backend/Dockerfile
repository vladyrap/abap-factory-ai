FROM python:3.11-slim

WORKDIR /app
# gcc/libpq para psycopg2; tesseract+poppler habilitan OCR de PDFs escaneados
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libpq-dev tesseract-ocr tesseract-ocr-spa poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Healthcheck sin curl (usa Python): marca el contenedor unhealthy si /health falla
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
