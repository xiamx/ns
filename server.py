"""
Serves the main html app and the REST api
"""
from os import environ
from flask import (Flask, render_template, request, jsonify,
                   abort, redirect, session)
from summarizer import generate_summary

app = Flask(__name__)


@app.route("/")
def main():
    """
    Render the main html app
    """
    if environ.get("REDIRECT"):
        print "Move to new domain"
        return redirect("http://ns.apps.xiamx.me" + "/", code=301)
    return render_template("main.html")


@app.route("/summarize", methods=['POST'])
def summarize():
    """
    Get a summary of given links subjected to limit of words
    Argument in JSON:
    {
      topic: "topic inputted by user",
      links: ["array of links"],
      words: 150 // words limit
    }
    """
    if environ.get("REDIRECT"):
        print "Move to new domain"
        return redirect("http://ns.apps.xiamx.me" + "/summarize", code=301)
    params = request.get_json()
    print "Summarize " + params["topic"] + " from " + str(params["links"])
    if not len(params["links"]) > 0:
        abort(400)
    summary = generate_summary.delay(params["links"], params["words"])
    session["summary_work"] = summary.task_id
    return jsonify({"status": "created"}), 201


@app.route("/getsummary")
def get_summary():
    summary = generate_summary.AsyncResult(session["summary_work"])
    if summary:
        if summary.ready():
            response = {"summary": summary.get(), "status": "done"}
            return jsonify(response)
        else:
            response = {"status": "working"}
            return jsonify(response)
    else:
        abort(400)


@app.route('/static/<path:path>')
def static_proxy(path):
    """
    Send static files
    """
    return app.send_static_file("static/" + path)

if __name__ == "__main__":
    if (environ.get("DEBUG")):
        app.debug = True
    app.secret_key = environ.get("SECRET_KEY")
    app.run(environ.get("IP", "0.0.0.0"), int(environ.get("PORT", "8080")))
