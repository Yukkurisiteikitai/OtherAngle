from flask import Flask, request, render_template, redirect, abort, Response
from urllib.parse import unquote, quote
from flask_cors import CORS
import requests
from markdown_it import MarkdownIt
import json


app = Flask(__name__)

CORS(app, resources={r"/*": {
    "origins": ["http://127.0.0.1:8030", "https://example.com", "http://127.0.0.1:8000","http://127.0.0.1:8120"],
    "methods": ["GET", "POST"],
    "allow_headers": [r"*"]
}})




reset = ""

# Initial content
content_dict = {
    'content1': reset,
    'content2': reset,
    'content3': reset,
    'view1': reset,
    'view2': reset,
    'view3': reset,
}

@app.route("/")
def site_start():
    return render_template("index.html", content_dict=content_dict, theme_input="")

# This route now just renders the page with the theme.
# The actual data loading is done by the frontend via streaming.
@app.route("/setForm")
def setForm():
    theme_input = request.args.get('theme', '')
    if len(theme_input) > 40:
        return {"ERROR": "OverThemeWords"}
    
    # Render the template with the theme. The page will then use JS to fetch the streams.
    return render_template("index.html", content_dict=content_dict, theme_input=theme_input)


@app.route("/stream-proxy")
def stream_proxy():
    theme = request.args.get('theme', '')
    if not theme:
        return Response("Missing 'theme' parameter", status=400)

    # URL-encode the theme parameter before passing it to the next service
    theme_encoded = quote(theme)
    # The URL to the FastAPI streaming endpoint
    url = f"http://127.0.0.1:8030/inference/type/theme?c={theme_encoded}"

    def generate():
        try:
            with requests.get(url, stream=True, timeout=300) as r:
                r.raise_for_status() # Raise an exception for bad status codes
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
        except requests.exceptions.RequestException as e:
            print(f"Error proxying stream: {e}")
            # Yield an error message to the client
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), content_type='application/x-ndjson')


# The old /req route is no longer needed for the new streaming implementation.
# You can keep it for other purposes or remove it.
@app.route("/req")
def old_req_route():
    return "This route is no longer used for the main functionality.", 404


#アプリ実行
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8120, debug=True)
