
# Start with a base image
FROM ubuntu:20.04

# Add the repository for the Intel graphics drivers
RUN echo "deb http://ppa.launchpad.net/oibaf/graphics-drivers/ubuntu focal main" >> /etc/apt/sources.list

# Update the package list and install the drivers
RUN apt-get update && apt-get install -y libgl1-mesa-dri libgl1-mesa-glx

# Install FFmpeg and the Intel hardware acceleration library
RUN apt-get install -y ffmpeg && apt-get install -y libva-intel-driver


FROM python:3.9.2
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH="/:$PYTHONPATH"

RUN apt-get -y update
RUN apt-get -y upgrade

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "service/manage.py", "migrate", "--settings=service.settings.production"]

CMD ["python", "service/manage.py", "runwavu", "--settings=service.settings.production"]