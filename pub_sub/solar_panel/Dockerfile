FROM python:3.10-slim-bullseye

WORKDIR /app

COPY main.py main.py
COPY run.json run.json 
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD [ "python", "-u", "main.py" ]
