FROM python:3.9-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the app port
EXPOSE 5000

# Start with Gunicorn: module:app_object
# Adjust workers/threads based on your CPU/memory
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
