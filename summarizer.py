"""
Celery Task that generates summary
"""
import gevent
from gevent import monkey
monkey.patch_all()
from celery import Celery
from os import environ
from newspaper import Article
import gc
import sumbasic

celery = Celery(__name__, broker=environ.get("REDIS_URL"))
celery.conf.update(
    CELERY_BROKER_URL=environ.get("REDIS_URL"),
    CELERY_RESULT_BACKEND=environ.get("REDIS_URL")
)

@celery.task()
def generate_summary(links, words):
    print "Generate Summary " + str(links)
    lines = []
    """
    >>> urls = ['www.google.com', 'www.example.com', 'www.python.org']
>>> jobs = [gevent.spawn(socket.gethostbyname, url) for url in urls]
>>> gevent.joinall(jobs, timeout=2)
>>> [job.value for job in jobs]
    """
    
    def download_and_clean(url):
        try:
            print "Download " + url
            article = Article(url)
            article.download()
            print "Parse " + url
            article.parse()
            text = article.text
            top_image = article.top_image
        except:
            print "Failed to get " + url
            text = ""
            top_image = ""
        return text, top_image
    
    jobs = [gevent.spawn(download_and_clean, url) for url in links[:4]]
    gevent.joinall(jobs, timeout=10)
    lines = [job.value[0] for job in jobs if job.value and job.value[0] and len(job.value[0]) > 100]
    top_images = [job.value[1] for job in jobs if job.value and job.value[1]]

    gc.collect()

    summary = sumbasic.orig(lines, words)
    print "Generate Summary complete for " + str(links)
    return summary, top_images
