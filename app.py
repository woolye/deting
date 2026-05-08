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

def log_ip(ip, ua="", all_headers=""):
    """Log IP to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] REAL IP: {ip} | UA: {ua[:50]}\n"
    
    # Write to temp file
    try:
        with open("/tmp/ips.log", "a") as f:
            f.write(log_line)
    except:
        pass
    
    # Print for Vercel logs (this appears in your dashboard)
    print(log_line.strip())
    return True

def get_real_ip(environ, headers):
    """Extract real IP from various Vercel headers"""
    
    # Priority order for Vercel real IP headers
    real_ip = None
    
    # 1. x-vercel-forwarded-for (most reliable for Vercel)
    vercel_fwd = headers.get('x-vercel-forwarded-for', '')
    if vercel_fwd:
        real_ip = vercel_fwd.split(',')[0].strip()
        if real_ip:
            return real_ip
    
    # 2. x-forwarded-for (standard proxy header)
    forwarded = headers.get('x-forwarded-for', '')
    if forwarded:
        # First IP is the original client
        ips = forwarded.split(',')
        real_ip = ips[0].strip()
        if real_ip and real_ip != '127.0.0.1':
            return real_ip
    
    # 3. cf-connecting-ip (Cloudflare)
    cf_ip = headers.get('cf-connecting-ip', '')
    if cf_ip:
        return cf_ip
    
    # 4. x-real-ip
    real = headers.get('x-real-ip', '')
    if real:
        return real
    
    # 5. true-client-ip
    true_ip = headers.get('true-client-ip', '')
    if true_ip:
        return true_ip
    
    # 6. Fallback to remote addr
    remote_addr = environ.get('REMOTE_ADDR', '')
    if remote_addr and remote_addr != '127.0.0.1':
        return remote_addr
    
    # 7. Last resort - log that we couldn't get real IP
    print("WARNING: Could not extract real IP, all headers:", dict(headers))
    return 'Unable to detect (check logs)'

def app(environ, start_response):
    """Vercel WSGI app function"""
    
    # Parse headers from environ
    headers = {}
    for key, value in environ.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').lower()
            headers[header_name] = value
    
    # Also check for non-HTTP_ prefixed headers
    if 'HTTP_X_FORWARDED_FOR' in environ:
        headers['x-forwarded-for'] = environ['HTTP_X_FORWARDED_FOR']
    if 'HTTP_X_VERCEL_FORWARDED_FOR' in environ:
        headers['x-vercel-forwarded-for'] = environ['HTTP_X_VERCEL_FORWARDED_FOR']
    if 'HTTP_X_REAL_IP' in environ:
        headers['x-real-ip'] = environ['HTTP_X_REAL_IP']
    if 'HTTP_CF_CONNECTING_IP' in environ:
        headers['cf-connecting-ip'] = environ['HTTP_CF_CONNECTING_IP']
    
    # Get user agent
    user_agent = headers.get('user-agent', 'Unknown')
    
    # Get real IP address
    real_ip = get_real_ip(environ, headers)
    
    # Print debug info to Vercel logs
    print(f"=== New Request ===")
    print(f"Headers received: {dict(list(headers.items())[:10])}")  # Print first 10 headers
    print(f"Extracted Real IP: {real_ip}")
    
    # Log the real IP
    log_ip(real_ip, user_agent)
    
    # Create HTML with IP (show real IP on screen)
    html = HTML_PAGE.replace("{{IP}}", real_ip)
    
    # Send response
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(html)))
    ]
    start_response(status, response_headers)
    return [html.encode('utf-8')]
