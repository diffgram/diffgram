FROM python:3.11.1-bullseye
LABEL python_version=python3.11.1

ENV DOCKER_CONTEXT=True

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate
RUN apt-get update
RUN apt-get install -y python3-dev
ADD local_dispatcher/requirements.txt /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt

ADD local_dispatcher/ /app/
ADD shared/ /app/
WORKDIR /app/

EXPOSE 8085
CMD python local_dispatch.py