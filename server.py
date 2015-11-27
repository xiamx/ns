"""
Serves the main html app and the REST api
"""
from os import environ
from flask import Flask, render_template, request, jsonify, abort
from summarizer import generate_summary

app = Flask(__name__)

@app.route("/")
def main():
    """
    Render the main html app
    """
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
    params = request.get_json()
    print "Summarize " + params["topic"] + " from " + str(params["links"])
    if not len(params["links"]) > 0:
        abort(400)
    summary = generate_summary.delay(params["links"], params["words"])
    response = {"summary": summary.get()}
    return jsonify(response)


@app.route('/static/<path:path>')
def static_proxy(path):
    """
    Send static files
    """
    return app.send_static_file("static/" + path)

if __name__ == "__main__":
    app.run(environ.get("IP", "0.0.0.0"), int(environ.get("PORT", "8080")))
