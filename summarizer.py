from celery import Celery
from os import environ
from newspaper import Article
import sumbasic

celery = Celery(__name__, broker=environ.get("REDIS_URL"))
celery.conf.update(
    CELERY_BROKER_URL=environ.get("REDIS_URL"),
    CELERY_RESULT_BACKEND=environ.get("REDIS_URL")
)

@celery.task()
def generate_summary(links, words):
    lines = []
    for url in links[:4]:
        try:
            article = Article(url)
            article.download()
            article.parse()
            if (len(article.text) > 100):
                lines.append(article.text)
        except:
            print "Failed to get " + url
            continue
    
    summary = sumbasic.orig(lines, words)
    return summary
