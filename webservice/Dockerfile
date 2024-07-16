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

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
