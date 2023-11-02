# Use the official Python image as a parent image
FROM python:3.11.4-slim-buster

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade setuptools
# Install PostgreSQL development files

RUN apt-get update && apt-get install -y libpq-dev && apt-get install -y python3-dev && apt-get install -y gcc
# Set the working directory
WORKDIR /app

# Install the python-dotenv library
RUN pip install python-dotenv

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip cache purge
RUN pip install --upgrade pip
# Install any other dependencies
RUN pip install -r requirements.txt

EXPOSE 5000
# Command to run your application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.wsgi:application"]
