from os import environ
from flask import Flask, render_template, request, jsonify, url_for
import sumbasic
from newspaper import Article
from celery import Celery
import lxml

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL=environ.get("REDIS_URL"),
    CELERY_RESULT_BACKEND=environ.get("REDIS_URL")
)
celery = make_celery(app)

@app.route("/")
def hello():
    # return "HI"
    return render_template("main.html")

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
    
    summary = sumbasic.orig(lines, words)
    return summary

@app.route("/summarize", methods=['POST'])
def summarize():
    params = request.get_json()
    print "Summarize " + params["topic"] + " from " + str(params["links"])
    summary = generate_summary.delay(params["links"], params["words"]) 
    response = { "summary": summary.get() }
    return jsonify(response)
    

@app.route('/static/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file("static/" + path)

if __name__ == "__main__":
    app.run(environ.get("IP", "0.0.0.0"), int(environ.get("PORT", "8080")))
    