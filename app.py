# app.py - Simple IP logger for Vercel

from datetime import datetime

# HTML page with video and IP display
HTML_PAGE = """<!DOCTYPE html>
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
        #ip-log {
            position: fixed;
            bottom: 10px;
            right: 10px;
            color: #0f0;
            background: rgba(0,0,0,0.6);
            padding: 4px 10px;
            border-radius: 5px;
            font-size: 10px;
            font-family: monospace;
            z-index: 999;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <button id="enter">ENTER SITE</button>
    <iframe id="vid" src="https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=1&controls=0&rel=0&mute=0" allow="autoplay; fullscreen"></iframe>
    <div id="ip-log">🌐 IP: <span id="ip-addr">{{IP}}</span></div>
    
    <script>
        let visitorIP = "{{IP}}";
        if (visitorIP && visitorIP !== "") {
            document.getElementById("ip-addr").innerText = visitorIP;
        }
        
        document.getElementById("enter").onclick = () => {
            document.getElementById("enter").style.display = "none";
            document.getElementById("vid").style.display = "block";
        };
    </script>
</body>
</html>"""

def log_ip(ip, ua=""):
    """Log IP to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] IP: {ip} | UA: {ua[:50]}\n"
    
    # Write to temp file
    try:
        with open("/tmp/ips.log", "a") as f:
            f.write(log_line)
    except:
        pass
    
    # Print for Vercel logs (this appears in your dashboard)
    print(log_line.strip())
    return True

def app(environ, start_response):
    """Vercel expects a WSGI app function named 'app'"""
    
    # Get IP from headers
    # Parse headers from environ
    headers = {}
    for key, value in environ.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').lower()
            headers[header_name] = value
    
    # Get user agent
    user_agent = headers.get('user-agent', 'Unknown')
    
    # Get real IP (check common headers)
    ip = '0.0.0.0'
    
    # Check x-forwarded-for
    forwarded = headers.get('x-forwarded-for', '')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    # Check vercel specific header
    elif headers.get('x-vercel-forwarded-for', ''):
        ip = headers.get('x-vercel-forwarded-for').split(',')[0].strip()
    # Check x-real-ip
    elif headers.get('x-real-ip', ''):
        ip = headers.get('x-real-ip')
    # Fallback to remote addr
    elif environ.get('REMOTE_ADDR'):
        ip = environ.get('REMOTE_ADDR')
    
    # Log the IP
    log_ip(ip, user_agent)
    
    # Create HTML with IP
    html = HTML_PAGE.replace("{{IP}}", ip)
    
    # Send response
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(html)))
    ]
    start_response(status, response_headers)
    return [html.encode('utf-8')]
