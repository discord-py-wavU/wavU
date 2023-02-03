
FROM python:3.9.2
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH="/:$PYTHONPATH"

RUN apt-get update && apt-get install -y \
    autoconf \
    automake \
    build-essential \
    libass-dev \
    libtool \
    pkg-config \
    git \
 && rm -rf /var/lib/apt/lists/*

# Download FFmpeg source code
RUN git clone https://github.com/FFmpeg/FFmpeg.git

# Build and install FFmpeg
WORKDIR /FFmpeg
RUN ./configure \
 && make \
 && make install

RUN cd

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "service/manage.py", "migrate", "--settings=service.settings.production"]

CMD ["python", "service/manage.py", "runwavu", "--settings=service.settings.production"]