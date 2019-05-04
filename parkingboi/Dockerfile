FROM python:3.7-alpine

LABEL maintainer="syndikaatti" \
      description="Parkingboi"

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

CMD ["./run.sh"]
