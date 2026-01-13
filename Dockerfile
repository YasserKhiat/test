FROM python:3.9-slim

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ .

# SECURITY FIX: Run as non-root user
RUN useradd -m myuser
USER myuser

EXPOSE 5000
CMD ["python", "app.py"]