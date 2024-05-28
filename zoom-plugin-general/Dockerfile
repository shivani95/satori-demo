# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the environment variables
# ENV PORT=8080

# Set environment variables
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/satori-ai-demo-571aba22c2f4.json

# Expose the port that the application will run on
EXPOSE $PORT

# Command to run the Flask application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app", "--timeout", "120"]
