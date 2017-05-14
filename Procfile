web: waitress-serve server:app
worker: celery -A summarizer.celery worker --autoscale=50,2 