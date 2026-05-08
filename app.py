# app.py - Simple IP logger that prints to Vercel logs

from datetime import datetime

# Simple HTML page
HTML = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            margin: 0;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: black;
            font-family: Arial;
        }
        #enter {
            font-size: 28px;
            padding: 18px 40px;
            border: 2px solid white;
            color: white;
            background: transparent;
            cursor: pointer;
            transition: 0.4s;
        }
        #enter:hover {
            background: white;
            color: black;
            transform: scale(1.1);
        }
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
            display: none;
        }
    </style>
</head>
<body>
    <button id="enter">ENTER SITE</button>
    <iframe id="vid" src="https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=1&controls=0&rel=0" allow="autoplay; fullscreen"></iframe>
    <script>
        document.getElementById("enter").onclick = () => {
            document.getElementById("enter").style.display = "none";
            document.getElementById("vid").style.display = "block";
        };
    </script>
</body>
</html>"""

def app(environ, start_response):
    # Get real IP from headers
    headers = dict([(k[5:].replace('_', '-').lower(), v) 
                    for k, v in environ.items() if k.startswith('HTTP_')])
    
    # Get IP
    ip = (headers.get('x-vercel-forwarded-for', '') or 
          headers.get('x-forwarded-for', '') or 
          environ.get('REMOTE_ADDR', 'unknown')).split(',')[0].strip()
    
    # PRINT TO LOGS - THIS IS WHERE REAL IP APPEARS
    print(f"REAL VISITOR IP: {ip} at {datetime.now()}")
    
    # Send response
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [HTML.encode()]
