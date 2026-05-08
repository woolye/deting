from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ip = self.headers.get("x-forwarded-for") or self.client_address[0]

        print("Visitor IP:", ip)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(b"""
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
            src="https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=1&mute=1"
            allow="autoplay; fullscreen"
            allowfullscreen>
          </iframe>
        </body>
        </html>
        """)
