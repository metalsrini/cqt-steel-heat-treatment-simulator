FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . /app/

# Set Python path to include the project root
ENV PYTHONPATH=/app

# Change to backend directory
WORKDIR /app/web_application/backend

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]