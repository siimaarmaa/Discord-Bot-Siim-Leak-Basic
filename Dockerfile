FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install the necessary system dependencies
RUN apt-get update && apt-get install -y \
    libffi-dev \
    libnacl-dev \
    libsodium-dev \
    python3-dev \
    build-essential \
    python3-audioop \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the container
COPY requirements.txt .

# Upgrade pip and install the Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Run the application
CMD ["python", "main.py"]

