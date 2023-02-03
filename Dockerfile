
FROM python:3.9.2
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH="/:$PYTHONPATH"

RUN apt-get -y update
RUN apt-get -y upgrade

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 957D2708A03A4626

# Update the package list and install necessary dependencies
RUN apt-get update && apt-get install -y software-properties-common

# Add the repository for the Intel graphics drivers
RUN add-apt-repository ppa:oibaf/graphics-drivers
RUN apt-get update

# Install the Intel graphics drivers
RUN apt-get install -y libgl1-mesa-dri libgl1-mesa-glx

# Install FFmpeg and the Intel hardware acceleration library
RUN apt-get install -y ffmpeg
RUN apt-get install -y libva-intel-driver

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "service/manage.py", "migrate", "--settings=service.settings.production"]

CMD ["python", "service/manage.py", "runwavu", "--settings=service.settings.production"]