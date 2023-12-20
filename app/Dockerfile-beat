FROM python:3.11.4-slim-buster

WORKDIR /app
RUN apt-get update && apt-get install -y libgl1-mesa-glx && apt-get install -y libglib2.0-0

RUN export PYTHONPATH=/lib/x86_64-linux-gnu/libGL.so.1:$PYTHONPATH
RUN pip install --upgrade setuptools
# Install PostgreSQL development files

RUN apt-get update && apt-get install -y libpq-dev && apt-get install -y python3-dev && apt-get install -y gcc
# Set the working directory

# Install the python-dotenv library
RUN pip install python-dotenv

COPY . /app

RUN pip cache purge
RUN pip install --upgrade pip
# Install any other dependencies
RUN pip install -r requirements.txt


CMD ["celery", "-A", "vcec_bk", "beat", "-l", "info"]