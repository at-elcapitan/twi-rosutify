FROM python:3.10-alpine

WORKDIR /opt/rosutify

COPY requirements.txt requirements.txt
COPY rosutify rosutify

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "rosutify"]