FROM python:3.11.1-bullseye
LABEL python_version=python3.11.1

RUN seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{}
RUN for i in {1..8}; do mkdir -p "/usr/share/man/man$i"; done
RUN apt-get update
RUN apt-get install -y libpq-dev python3-dev build-essential postgresql postgresql-contrib ffmpeg libsm6 libxext6
ADD eventhandlers/requirements.txt /app/
RUN pip3 install --upgrade pip
RUN pip3 install setuptools_rust
RUN pip3 install --no-build-isolation tokenizers torch==2.0
RUN apt-get install -y curl
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y  # Add this line
ENV PATH="/root/.cargo/bin:${PATH}"

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip3 install --no-build-isolation  -r /app/requirements.txt
ADD eventhandlers/ /app/
ADD shared /app/shared
ENV TRANSFORMERS_CACHE=/tmp/
ENV HF_HOME=/tmp/
WORKDIR /app/
EXPOSE 8086


CMD exec newrelic-admin run-program python main.py