# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Arguments to skip venv and pycache
ARG SKIP_PYCACHE
ARG SKIP_VENV

# Set environment variable to skip pycache if specified
ENV PYTHONDONTWRITEBYTECODE=${SKIP_PYCACHE}
ENV PIP_NO_CACHE_DIR=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Ensure the .env file is copied (if needed for local testing)
# COPY .env .

# Command to run the scheduler
CMD ["python", "scheduler.py"]
