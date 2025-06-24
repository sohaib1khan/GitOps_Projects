# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and assets
COPY main.py .
# COPY questions.json .
# COPY users.json .
# COPY progress.json .
# COPY flashcards.json .
# COPY flashcard_progress.json .
COPY templates/ ./templates/
COPY static/ ./static/

# Expose the port the app runs on
EXPOSE 5019

# Command to run the application
CMD ["python", "main.py"]
