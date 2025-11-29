# Dockerfile
FROM python:3.10-slim

# Create working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy the rest of the project
COPY . .

# Expose port (required by Hugging Face)
EXPOSE 7860

# Default command: run Flask app via Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
