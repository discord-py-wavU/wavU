
FROM python:3.9.2
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH="/:$PYTHONPATH"

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "service/manage.py", "migrate", "--settings=service.settings.production"]

CMD ["python", "service/manage.py", "runwavu", "--settings=service.settings.production"]