web: gunicorn server:app --log-file=-
worker: celery -A summarizer.celery worker --autoscale=50,2 -P gevent