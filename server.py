"""Serves the main html app and the REST api."""
from os import environ

from datetime import datetime, timedelta
from flask import (Flask, render_template, request, jsonify,
                   abort, redirect)
from summarizer import generate_summary
from database import db, Summary
from peewee import DoesNotExist

app = Flask(__name__)


@app.route("/")
def main():
    """Return html render of the main app."""
    if environ.get("REDIRECT") == "1":
        print("Move to new domain")
        return redirect("http://ns.apps.xiamx.me" + "/", code=301)
    return render_template("main.html")


@app.route("/summarize", methods=['POST'])
def summarize():
    """
    Get a summary of given links subjected to limit of words.

    Argument in JSON:
    {
      topic: "topic inputted by user",
      words: 150 // words limit
    }

    Return 201 if request is queued, otherwise return 4xx.

    """
    if environ.get("REDIRECT") == "1":
        print("Move to new domain")
        return redirect("http://ns.apps.xiamx.me" + "/summarize", code=301)
    params = request.get_json()

    print("Summarize %s" % params["topic"])

    try:
        cached_summary = Summary.select().where(
            Summary.topic == params["topic"],
            Summary.last_updated.between(
                datetime.today() - timedelta(days=3),
                datetime.today()
            )
        ).order_by(Summary.last_updated.desc()).get()
        print("Summary found in database")
        return jsonify({
            "summary": cached_summary.summary,
            "images": cached_summary.images,
            "links": cached_summary.links,
            "names": cached_summary.names,
            "status": "done"
        }), 200
    except DoesNotExist:
        summary = generate_summary.delay(params["topic"], params["words"])
        tid = summary.task_id
        return jsonify({"status": "created", "task": tid}), 201


@app.route("/getsummary/<tid>")
def get_summary(tid):
    """Return summary given the task id."""
    summary = generate_summary.AsyncResult(tid)
    if summary:
        if summary.ready():
            summary = summary.get()
            response = {"summary": summary[0],
                        "images": summary[1],
                        "links": summary[2],
                        "names": summary[3],
                        "status": "done"}

            db_summary = Summary(
                topic=summary[4],
                word_limit=summary[5],
                summary=summary[0],
                last_updated=datetime.now(),
                images=summary[1],
                links=summary[2],
                names=summary[3]
            )
            db_summary.save()

            return jsonify(response)
        else:
            response = {"status": "working"}
            return jsonify(response)
    else:
        abort(400)


@app.route('/static/<path:path>')
def static_proxy(path):
    """Return static files."""
    return app.send_static_file("static/" + path)

if __name__ == "__main__":
    db.connect()
    if environ.get("DEBUG"):
        app.debug = True
    app.secret_key = environ.get("SECRET_KEY")
    app.run(environ.get("IP", "0.0.0.0"), int(environ.get("PORT", "8080")))
