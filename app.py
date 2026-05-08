from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!doctype html>
    <html>
    <head>
      <style>
        html, body {
          margin: 0;
          height: 100%;
          background: black;
          overflow: hidden;
        }
        iframe {
          width: 100vw;
          height: 100vh;
          border: none;
        }
      </style>
    </head>
    <body>
      <iframe
        src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&controls=0"
        allow="autoplay; fullscreen"
        allowfullscreen>
      </iframe>
    </body>
    </html>
    """

app = app
