FROM python:3.10-slim-bullseye

WORKDIR /app

COPY main.py main.py
COPY application_default_credentials.json application_default_credentials.json
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD [ "python", "-u", "main.py" ]
