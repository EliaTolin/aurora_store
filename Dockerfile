# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages
RUN pip install -r requirements.txt

# Set the environment variable for Django settings module
ENV DJANGO_SETTINGS_MODULE=aurorastore.settings

# Expose the default port for Django
EXPOSE 8000

# Run the command to start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]