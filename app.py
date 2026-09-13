from flask import Flask, render_template, request, jsonify, Response
import requests
import subprocess
import tempfile
import os

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/extract", methods=["POST"])
def extract():

    data = request.get_json() or {}

    url = data.get("url", "").strip()
    mode = data.get("mode", "mp4")

    if not url.startswith(("http://", "https://")):
        return jsonify({
            "success": False,
            "message": "Please provide a valid URL."
        }), 400

    try:

        media = requests.get(
            url,
            stream=True,
            timeout=30
        )

        media.raise_for_status()


        # MP4 DOWNLOAD
        if mode == "mp4":

            content_type = media.headers.get(
                "Content-Type",
                "application/octet-stream"
            )

            def generate():

                for chunk in media.iter_content(
                    chunk_size=8192
                ):

                    if chunk:
                        yield chunk


            return Response(

                generate(),

                content_type=content_type,

                headers={
                    "Content-Disposition":
                    'attachment; filename="media.mp4"'
                }

            )


        # MP3 CONVERSION
        elif mode == "mp3":

            with tempfile.TemporaryDirectory() as temp_dir:

                input_file = os.path.join(
                    temp_dir,
                    "input_media"
                )

                output_file = os.path.join(
                    temp_dir,
                    "audio.mp3"
                )


                # Save downloaded media temporarily

                with open(input_file, "wb") as file:

                    for chunk in media.iter_content(
                        chunk_size=8192
                    ):

                        if chunk:
                            file.write(chunk)


                # Convert using FFmpeg

                subprocess.run(
                    [
                        "ffmpeg",
                        "-i",
                        input_file,
                        "-vn",
                        "-codec:a",
                        "libmp3lame",
                        "-q:a",
                        "2",
                        output_file
                    ],

                    check=True,

                    capture_output=True
                )


                with open(
                    output_file,
                    "rb"
                ) as file:

                    mp3_data = file.read()


                return Response(

                    mp3_data,

                    mimetype="audio/mpeg",

                    headers={
                        "Content-Disposition":
                        'attachment; filename="audio.mp3"'
                    }

                )


        else:

            return jsonify({
                "success": False,
                "message": "Invalid mode."
            }), 400


    except Exception as error:

        print(error)

        return jsonify({
            "success": False,
            "message":
            "Could not process this media URL."
        }), 500


if __name__ == "__main__":
    app.run()
