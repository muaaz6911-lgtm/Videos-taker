from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/extract", methods=["POST"])
def extract():

    data = request.get_json()

    url = data.get("url")
    mode = data.get("mode")

    if not url:
        return jsonify({
            "success": False,
            "message": "Please provide a URL"
        }), 400

    return jsonify({
        "success": True,
        "message": f"Python backend received your {mode} request!"
    })


if __name__ == "__main__":
    app.run()
