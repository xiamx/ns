from os import environ
from flask import Flask, render_template, request, jsonify, url_for
from celery import Celery
import lxml
from summarizer import generate_summary

app = Flask(__name__)

@app.route("/")
def hello():
    # return "HI"
    return render_template("main.html")

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
    