web: gunicorn server:app --log-file=-
worker: celery -A summarizer.celery worker --concurrency=2