# Use the official lightweight Python 3.13 image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Install system dependencies (required for Pillow/PyMuPDF C-extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit's port
EXPOSE 8501

# Add a healthcheck to verify Streamlit is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch Streamlit
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]