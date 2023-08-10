FROM ubuntu:22.04
LABEL python_version=python3.11.1

ENV DOCKER_CONTEXT=True

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get remove --purge python3 python3.6 python3-pip -y
RUN apt-get autoremove -y
RUN apt-get update -y && apt-get upgrade -y

RUN apt-get -y install ffmpeg python3.11 python3-pip libpq-dev python3.11-venv python3.11-distutils python3.11-dev git python3-setuptools libgdal-dev python3-lxml libxslt-dev
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal
RUN export C_INCLUDE_PATH=/usr/include/gdal
## Install FFMPEG V 4.3
RUN ffmpeg -version
RUN apt-get -y install libxml2-dev libxslt1-dev
#RUN mv /usr/local/lib/libxml2* ~
ADD walrus/requirements.txt /app/

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

RUN python3 -m ensurepip --upgrade
RUN pip3 install --upgrade pip



RUN pip3 install lxml
RUN gdal-config --version

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
RUN gdal-config --version
RUN pip3 install GDAL==3.4.1
RUN pip3 install -r /app/requirements.txt

ADD walrus/ /app/
ADD shared /app/shared
WORKDIR /app/


ENV PYTHONPATH=/app
ENV NEW_RELIC_CONFIG_FILE=/app/newrelic.ini
EXPOSE 8080

ENTRYPOINT gunicorn --bind :8080 --timeout 120 --worker-class sync --workers 3 --no-sendfile main:app