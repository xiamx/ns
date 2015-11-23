from os import environ
from flask import Flask, render_template, request, jsonify, url_for
import sumbasic
from newspaper import Article
from nltk import downloader

packages = ['wordnet', 'punkt', 'stopwords']
downloader.download(packages)

app = Flask(__name__)

@app.route("/")
def hello():
    # return "HI"
    return render_template("main.html")

@app.route("/summarize", methods=['POST'])
def summarize():
    params = request.get_json(cache=True)
    print params["links"]
    lines = []
    for url in params["links"][:4]:
        article = Article(url)
        article.download()
        article.parse()
        if (len(article.text) > 100):
            lines.append(article.text)
        print lines
    
    summary = sumbasic.orig(lines, int(params["words"]))
    response = { "summary": summary }
    return jsonify(response)
    

@app.route('/static/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file("static/" + path)

if __name__ == "__main__":
    app.debug = True
    app.run(environ.get("IP", "0.0.0.0"), int(environ.get("PORT", "8080")))
    