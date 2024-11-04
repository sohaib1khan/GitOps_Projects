# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any necessary dependencies
RUN pip install --no-cache-dir flask

# Expose the application's port
EXPOSE 5027

# Start the application using python
CMD ["python", "app.py"]

# Build the Docker image