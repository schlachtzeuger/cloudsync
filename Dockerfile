FROM python:3-bookworm

RUN apt update && \
    apt install -y rclone

RUN python -m venv my-venv

RUN my-venv/bin/pip install watchdog

ADD cloudsync.py /

ENTRYPOINT ["/my-venv/bin/python", "/cloudsync.py"]
