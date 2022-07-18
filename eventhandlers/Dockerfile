FROM python:3.7.2-slim
LABEL python_version=python3.7.2

RUN seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{}
RUN for i in {1..8}; do mkdir -p "/usr/share/man/man$i"; done
RUN apt-get update
RUN apt-get install -y libpq-dev python3-dev build-essential postgresql postgresql-contrib ffmpeg libsm6 libxext6
ADD eventhandlers/requirements.txt /app/
RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt
ADD eventhandlers/ /app/
ADD shared /app/shared
ENV TRANSFORMERS_CACHE=/tmp/
ENV HF_HOME=/tmp/
WORKDIR /app/
EXPOSE 8086

CMD ["python", "main.py"]