from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ip = self.headers.get("x-forwarded-for")

        # log IP (shows in Vercel logs)
        print("IP:", ip)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html = """
        <!doctype html>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>
            html, body {
              margin: 0;
              height: 100%;
              background: black;
              display: flex;
              justify-content: center;
              align-items: center;
              flex-direction: column;
              color: white;
              font-family: sans-serif;
            }

            iframe {
              width: 100vw;
              height: 100vh;
              border: none;
              display: none;
            }

            button {
              padding: 15px 25px;
              font-size: 18px;
              cursor: pointer;
            }
          </style>
        </head>
        <body>

          <button onclick="start()">Click to Start Video + Sound</button>

          <iframe id="vid"
            src="https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=1&controls=0&rel=0"
            allow="autoplay; fullscreen"
            allowfullscreen>
          </iframe>

          <script>
            function start() {
              document.querySelector("button").style.display = "none";
              document.getElementById("vid").style.display = "block";
            }
          </script>

        </body>
        </html>
        """

        self.wfile.write(html.encode())
