# Dockerfile for Perf-Chart-Gen Streamlit Application
# Optimized for production deployment with iframe embedding support
#
# Build command: docker build -t perf-chart-gen:latest .
# Run command: docker run -p 8501:8501 perf-chart-gen:latest

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for matplotlib and reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY athlete_report_streamlit.py .
COPY athlete_report.py .
COPY security.py .
COPY team_report_generator.py .
COPY sample_athletes.csv .
COPY sample_athletes_in_season.csv .

# Copy Streamlit configuration
COPY .streamlit/ .streamlit/

# Create directories for generated reports and logs
RUN mkdir -p /app/reports /app/logs

# Expose Streamlit default port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501/_stcore/health')" || exit 1

# Run Streamlit application
CMD ["streamlit", "run", "athlete_report_streamlit.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none", \
     "--browser.gatherUsageStats=false"]
