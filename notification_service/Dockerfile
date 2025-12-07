FROM python:3.11-slim
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY ./app /app/app
COPY ./start.sh /start.sh
COPY ./start-celery.sh /start-celery.sh
RUN chmod +x /start.sh /start-celery.sh
EXPOSE 8001
CMD ["/start.sh"]
