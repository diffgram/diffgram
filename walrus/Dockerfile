FROM jrottenberg/ffmpeg:4.3.1-ubuntu1804
LABEL python_version=python3.7.2

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate


RUN apt-get update -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get remove --purge python3 -y
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get -y install python3.7.2 python3-pip libpq-dev python3.7-dev git python3-setuptools

## Install FFMPEG V 4.3
RUN ffmpeg -version
ADD walrus/requirements.txt /app/
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
RUN pip3 install --upgrade pip
RUN python3.7 --version
RUN python3 --version
RUN pip3 install -r /app/requirements.txt

ADD walrus/ /app/
ADD shared /app/shared
WORKDIR /app/
ENV PYTHONPATH=/app
ENV NEW_RELIC_CONFIG_FILE=/app/newrelic.ini
#CMD exec gunicorn --bind :$PORT --timeout 120 --worker-class eventlet --workers 3 --no-sendfile --config python:my_conf main:app
EXPOSE 8080

ENTRYPOINT gunicorn --bind :8080 --timeout 120 --worker-class sync --workers 5 --no-sendfile main:app