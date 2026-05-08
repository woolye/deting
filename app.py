# app.py - IP logger with external API

from datetime import datetime
import urllib.request
import json

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

def send_to_ip_api(ip, user_agent):
    """Send IP to ipapi.co or similar logging service"""
    try:
        # Option 1: Use ipapi.co to get IP details (free, no key needed)
        url = f"https://ipapi.co/{ip}/json/"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            # Log the detailed info to Vercel console
            print(f"IP DETAILS - Country: {data.get('country_name', 'N/A')}, City: {data.get('city', 'N/A')}, ISP: {data.get('org', 'N/A')}")
        return True
    except Exception as e:
        print(f"Failed to get IP details: {e}")
        return False

def log_ip_to_webhook(ip, user_agent):
    """Send IP to a webhook logging service (like webhook.site or custom endpoint)"""
    try:
        # You can replace this with your own webhook URL
        # For testing, we'll just print it
        print(f"LOGGING IP: {ip} at {datetime.now()}")
        
        # Optional: Send to a free logging service like webhook.site
        # webhook_url = "https://webhook.site/your-unique-url"
        # data = json.dumps({"ip": ip, "timestamp": str(datetime.now()), "ua": user_agent}).encode()
        # req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json'})
        # urllib.request.urlopen(req, timeout=5)
        
        return True
    except Exception as e:
        print(f"Webhook error: {e}")
        return False

def log_ip(ip, ua=""):
    """Save IP to file and print with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] VISITOR IP: {ip} | UA: {ua[:80]}\n"
    
    # Write to temp file
    try:
        with open("/tmp/visitors.log", "a") as f:
            f.write(log_line)
    except:
        pass
    
    # Print to Vercel logs (THIS IS WHERE YOU SEE REAL IPS)
    print("=" * 50)
    print(log_line.strip())
    print("=" * 50)
    
    return True

def get_real_ip(environ, headers):
    """Extract real IP from Vercel headers"""
    
    # Try vercel-forwarded-for first
    vercel_fwd = headers.get('x-vercel-forwarded-for', '')
    if vercel_fwd:
        ip = vercel_fwd.split(',')[0].strip()
        if ip and ip != '127.0.0.1':
            return ip
    
    # Try x-forwarded-for
    forwarded = headers.get('x-forwarded-for', '')
    if forwarded:
        ips = forwarded.split(',')
        ip = ips[0].strip()
        if ip and ip != '127.0.0.1':
            return ip
    
    # Try cf-connecting-ip (Cloudflare)
    cf_ip = headers.get('cf-connecting-ip', '')
    if cf_ip:
        return cf_ip
    
    # Try x-real-ip
    real = headers.get('x-real-ip', '')
    if real:
        return real
    
    # Fallback - log all headers for debugging
    print("DEBUG - All headers received:")
    for k, v in headers.items():
        print(f"  {k}: {v}")
    
    return 'Unknown-IP-Check-Logs'

def app(environ, start_response):
    """Vercel WSGI app function"""
    
    # Parse headers
    headers = {}
    for key, value in environ.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').lower()
            headers[header_name] = value
    
    # Also check raw headers
    if 'HTTP_X_FORWARDED_FOR' in environ:
        headers['x-forwarded-for'] = environ['HTTP_X_FORWARDED_FOR']
    if 'HTTP_X_VERCEL_FORWARDED_FOR' in environ:
        headers['x-vercel-forwarded-for'] = environ['HTTP_X_VERCEL_FORWARDED_FOR']
    if 'HTTP_X_REAL_IP' in environ:
        headers['x-real-ip'] = environ['HTTP_X_REAL_IP']
    
    # Get user agent
    user_agent = headers.get('user-agent', 'Unknown')
    
    # Get real IP
    real_ip = get_real_ip(environ, headers)
    
    # Log the IP (this appears in Vercel function logs)
    log_ip(real_ip, user_agent)
    
    # Optional: Send to external API for more details
    send_to_ip_api(real_ip, user_agent)
    
    # Create HTML with IP
    html = HTML_PAGE.replace("{{IP}}", real_ip)
    
    # Send response
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(html)))
    ]
    start_response(status, response_headers)
    return [html.encode('utf-8')]
