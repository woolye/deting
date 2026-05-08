from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ip = self.headers.get("x-forwarded-for")

        # log IP to Vercel logs (THIS is what actually works)
        print("Visitor IP:", ip)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html = """
        <!doctype html>
        <html>
        <head>
          <style>
            html, body {
              margin: 0;
              height: 100%;
              overflow: hidden;
              background: black;
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
            src="https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=1&controls=0&mute=1"
            allow="autoplay; fullscreen"
            allowfullscreen>
          </iframe>
        </body>
        </html>
        """

        self.wfile.write(html.encode())
