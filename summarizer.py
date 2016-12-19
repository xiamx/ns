"""Celery Task that generates summary."""

import gevent
from gevent import monkey
monkey.patch_all()
from celery import Celery
from os import environ
from newspaper import Article
import gc
import sumbasic
import traceback
import requests
import urllib.request, urllib.parse, urllib.error

celery = Celery(__name__, broker=environ.get("RABBITMQ_URL") or "amqp://ns:ns@localhost:5672//")
celery.conf.update(
    CELERY_BROKER_URL=environ.get("RABBITMQ_URL") or "amqp://ns:ns@localhost:5672//",
    CELERY_RESULT_BACKEND=environ.get("RABBITMQ_URL") or "amqp://ns:ns@localhost:5672//"
)

API_ROOT = 'https://api.cognitive.microsoft.com/bing/v5.0/news/search'
API_KEY = environ.get("BING_API")


@celery.task()
def generate_summary(topic, words):
    """Return summary of the topic subjected to word limit."""
    print("Generate Summary %s" % topic)

    def query_links(topic):

        query = urllib.parse.urlencode({
            "q": "'" + topic + "'",
            "count": 4
        })
        headers = {
            "Ocp-Apim-Subscription-Key": API_KEY
        }
        url = API_ROOT + "?%s" % query
        r = requests.get(url, headers=headers)
        return r

    query_job = gevent.spawn(query_links, topic)
    gevent.joinall([query_job],5000)
    result = query_job.value.json()
    links = [x["url"] for x in result["value"]]
    names = [x["name"] for x in result["value"]]

    lines = []

    def download_and_clean(url):
        try:
            print("Download " + url)
            article = Article(url)
            article.download()
            print("Parse " + url)
            article.parse()
            text = article.text
            top_image = article.top_image
        except:
            print("Failed to get " + url)
            text = ""
            top_image = ""
        return text, top_image

    jobs = [gevent.spawn(download_and_clean, url) for url in links[:4]]
    gevent.joinall(jobs, timeout=10)
    lines = [job.value[0] for job in jobs if job.value and job.value[0] and len(job.value[0]) > 100]
    top_images = [job.value[1] for job in jobs if job.value and job.value[1]]

    gc.collect()
    try:
        summary = sumbasic.orig(lines, words)
    except ValueError:
        print("Generate Summary failed for " + str(links))
        traceback.print_exc()
        summary = "Generating summary failed"
    print("Generate Summary complete for " + str(links))
    return summary, top_images, links, names, topic, words
