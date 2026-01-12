# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 7860 available to the world outside this container
# Hugging Face Spaces uses port 7860 by default
EXPOSE 7860

# Run uvicorn when the container launches
# Using 0.0.0.0 to listen on all interfaces
# Using port 7860 for compatibility with standard HF Spaces, but can be overridden
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
