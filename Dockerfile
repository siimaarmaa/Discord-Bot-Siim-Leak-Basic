FROM python

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN --mount=type=secret,id=token cat /run/secrets/token \
    --mount=type=secret,id=guild cat /run/secrets/guild

# Copy the application code to the container
COPY . .

# Run the application
CMD ["python", "main.py"]
