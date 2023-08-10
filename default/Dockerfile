FROM python:3.11.1-bullseye
LABEL python_version=python3.11.1

ENV DOCKER_CONTEXT=True

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate
RUN seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{}
RUN for i in {1..8}; do mkdir -p "/usr/share/man/man$i"; done
RUN apt-get update
RUN apt-get install -y libpq-dev python3-dev build-essential postgresql postgresql-contrib
ADD default/requirements.txt /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt

ADD default/ /app/
ADD shared /app/shared

WORKDIR /app/
RUN ["chmod", "+x", "/app/db-init.sh"]

EXPOSE 8080
CMD exec gunicorn --bind :8080 --timeout 120 --worker-class sync --workers 5 --no-sendfile main:app