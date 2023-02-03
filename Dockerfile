
FROM python:3.9.2
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH="/:$PYTHONPATH"

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y software-properties-common && \
    add-apt-repository ppa:oibaf/graphics-drivers && \
    apt-get update && \
    apt-get install -y libgl1-mesa-dri libgl1-mesa-glx \
RUN apt-get install -y ffmpeg && apt-get install -y libva-intel-driver

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "service/manage.py", "migrate", "--settings=service.settings.production"]

CMD ["python", "service/manage.py", "runwavu", "--settings=service.settings.production"]