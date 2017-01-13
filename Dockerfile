FROM python:3.5

ADD requirements.txt /
ADD app.py /
ADD config.json /
WORKDIR /

RUN pip install -r ./requirements.txt

ENV REDIS_HOST redis

CMD ["python", "./app.py"]
