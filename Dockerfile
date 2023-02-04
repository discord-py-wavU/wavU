
FROM python:3.9.2
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH="/:$PYTHONPATH"

RUN apt-get -y update
RUN apt-get -y upgrade

RUN apt-get install -y software-properties-common
RUN  apt-get install -y libva-dev i965-va-driver-shader

RUN add-apt-repository ppa:jonathonf/ffmpeg-4
RUN apt-get update

RUN apt-get install -y ffmpeg

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "service/manage.py", "migrate", "--settings=service.settings.production"]

CMD ["python", "service/manage.py", "runwavu", "--settings=service.settings.production"]