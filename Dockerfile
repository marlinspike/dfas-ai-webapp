# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
# COPY . /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
# RUN pip install -r requirements.txt
RUN python -m pip install uvicorn


# Expose the port the app will run on
EXPOSE 80

# Command to run the FastAPI app with Gunicorn and UvicornWorker
CMD ["gunicorn", "--config", "./gunicorn.conf.py", "main:app"]

