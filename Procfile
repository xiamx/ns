web: gunicorn server:app --log-file=-
worker: celery -A server.celery worker