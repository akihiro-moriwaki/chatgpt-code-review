FROM python:3.11-slim

ENV ROOT_PATH=/usr/src/app

WORKDIR $ROOT_PATH
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
COPY main.py /main.py
RUN chmod 755 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
