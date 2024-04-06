FROM python:3.11.4-slim-buster

RUN pip install --upgrade setuptools

RUN apt-get update && apt-get install -y libgl1-mesa-glx && apt-get install -y libpq-dev && apt-get install -y python3-dev && apt-get install -y gcc && apt-get install -y libglib2.0-0 

RUN apt-get update && \
    apt-get install -y \
    libxcb-shm0 \
    libxrandr2 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libasound2 \
    libxrender1 \
    libfreetype6 \
    libfontconfig1 \
    libdbus-1-3

# set work directory
WORKDIR /usr/src/app


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .

RUN mkdir -p /home/app/.cache/ms-playwright && chmod -R 777 /home/app/.cache/ms-playwright

RUN pip install -r requirements.txt


COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
# copy project
COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]