FROM python:3.11-slim

RUN pip install --no-cache-dir flower==1.2.0 celery==5.3.1

EXPOSE 5555

# Для flower 1.2.0 используем --host вместо --address
CMD ["python", "-m", "flower", \
     "--broker=redis://redis:6379/1", \
     "--host=0.0.0.0", \
     "--port=5555"]
