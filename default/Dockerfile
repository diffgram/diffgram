# Use the official Python 3.11.1 image as the base image
FROM python:3.11.1-bullseye

# Set a label for the image with the Python version
LABEL python_version=python3.11.1

# Set an environment variable for the Docker context
ENV DOCKER_CONTEXT=True

# Set up the man directories for the man pages
RUN seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{}
RUN for i in {1..8}; do mkdir -p "/usr/share/man/man$i"; done

# Update the package lists for upgrades and new package installations
RUN apt-get update

# Install necessary packages for the application
RUN apt-get install -y libpq-dev python3-dev build-essential postgresql postgresql-contrib

# Copy the requirements.txt file from the default directory to the app directory
ADD default/requirements.txt /app/

# Upgrade pip to the latest version
RUN pip3 install --upgrade pip

# Install the required packages from the requirements.txt file
RUN pip3 install -r /app/requirements.txt

# Copy the default directory and shared directory to the app directory
ADD default/ /app/
ADD shared /app/shared

# Set the working directory to the app directory
WORKDIR /app/

# Make the db-init.sh script executable
RUN ["chmod", "+x", "/app/db-init.sh"]

# Expose port 8080 for the application
EXPOSE 8080

# Set the default command to run the application using Gunicorn
CMD exec gunicorn --bind :8080 --timeout 120 --worker-class sync --workers 5 --no-sendfile main:app
