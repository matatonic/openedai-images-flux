FROM python:3.11-slim
# For qint4 support, 2x docker image
#FROM nvidia/cuda:12.1.0-devel-ubuntu22.04
RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential python3-pip python-is-python3 python3-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir config models lora
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY config/lib /app/config/
COPY *.py *.json LICENSE /app/

ENV CLI_COMMAND="python images.py"
CMD $CLI_COMMAND
