FROM python:3.9

RUN rm -rf /var/cache/apk && \
    rm -rf tmp/cache

RUN mkdir /app

WORKDIR /app
ADD . /app/

RUN pip install -r requirements.txt

CMD ["python", "/app/main.py"]