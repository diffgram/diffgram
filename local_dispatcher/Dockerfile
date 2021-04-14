FROM python:3.7.2-slim
LABEL python_version=python3.7.2

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
#CMD exec gunicorn --bind :$PORT --timeout 120 --worker-class eventlet --workers 3 --no-sendfile --config python:my_conf main:app
EXPOSE 8085
CMD python local_dispatch.py