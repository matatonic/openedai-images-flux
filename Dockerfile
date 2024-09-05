FROM python:3.11-slim

WORKDIR /app
RUN mkdir config
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY *.py *.json LICENSE /app/
COPY config/*.json /app/config/

ENV CLI_COMMAND="python images.py"
CMD $CLI_COMMAND
