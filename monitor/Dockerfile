# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and locales
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    locales \
    && sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && locale-gen pt_BR.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Set locale environment variables
ENV LANG pt_BR.UTF-8
ENV LC_ALL pt_BR.UTF-8
ENV LANGUAGE pt_BR:pt
ENV TZ=America/Sao_Paulo

# Copy application files
COPY requirements.txt .
COPY config.ini .
COPY simple_monitor.py .

# Create logs directory
RUN mkdir -p logs

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the monitor
CMD ["python", "simple_monitor.py"]
