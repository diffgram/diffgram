FROM circleci/python:3.7-node

LABEL python_version=python3.7
USER root
RUN apt-get install -y software-properties-common
RUN  apt-get update && add-apt-repository ppa:jonathonf/ffmpeg-4 \
    && apt-get install libgbm-dev ffmpeg python-opencv