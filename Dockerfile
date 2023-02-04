
FROM python:3.9.2
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH="/:$PYTHONPATH"

RUN apt-get update && apt-get install -y curl
RUN curl https://gist.githubusercontent.com/feedsbrain/0191516b5625b577c2b14241cff4fe30/raw > script.sh
RUN chmod +x script.sh
RUN ./ffmpeg-qsv.sh

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "service/manage.py", "migrate", "--settings=service.settings.production"]

CMD ["python", "service/manage.py", "runwavu", "--settings=service.settings.production"]