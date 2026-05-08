# app.py - Simple IP logger + video page for Vercel

import json
from datetime import datetime

# HTML page with the video and IP display
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
        #ip-status {
            position: fixed;
            bottom: 10px;
            right: 10px;
            color: #0f0;
            background: rgba(0,0,0,0.5);
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 11px;
            font-family: monospace;
            z-index: 999;
        }
    </style>
</head>
<body>
    <button id="enter">ENTER SITE</button>
    <iframe id="vid" src="https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=1&controls=0&rel=0&mute=0" allow="autoplay; fullscreen"></iframe>
    <div id="ip-status">📡 IP: <span id="ip-display">detecting...</span></div>
    
    <script>
        // Get IP from server-side injected value
        let myIp = "{{IP_ADDRESS}}";
        if (myIp && myIp !== "") {
            document.getElementById("ip-display").innerText = myIp;
        } else {
            // Fallback: get IP from free API
            fetch('https://api.ipify.org?format=json')
                .then(r => r.json())
                .then(data => {
                    document.getElementById("ip-display").innerText = data.ip;
                });
        }
        
        document.getElementById("enter").onclick = () => {
            document.getElementById("enter").style.display = "none";
            document.getElementById("vid").style.display = "block";
        };
    </script>
</body>
</html>"""

def log_ip(ip, user_agent=""):
    """Save IP to log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] IP: {ip} | UA: {user_agent}\n"
    
    # Save to /tmp/ip.log (works on Vercel)
    with open("/tmp/ip.log", "a") as f:
        f.write(log_entry)
    
    # Also print for Vercel logs
    print(log_entry.strip())
    return True

def handler(request, context):
    """Main Vercel function handler"""
    try:
        # Get headers as dict
        headers = dict(request.headers)
        
        # Get real IP address
        ip = headers.get('x-forwarded-for', '').split(',')[0].strip()
        if not ip:
            ip = headers.get('x-vercel-forwarded-for', '').split(',')[0].strip()
        if not ip:
            ip = headers.get('x-real-ip', '')
        if not ip:
            ip = '0.0.0.0'
        
        # Get user agent
        ua = headers.get('user-agent', 'Unknown')
        
        # Log the IP
        log_ip(ip, ua)
        
        # Create HTML with IP injected
        html = HTML_PAGE.replace("{{IP_ADDRESS}}", ip)
        
        # Return success response
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": html
        }
        
    except Exception as e:
        # Return simple error page
        error_html = f"""<!DOCTYPE html>
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:50px">
            <h1>Site is live!</h1>
            <button onclick="location.reload()" style="padding:15px 30px">Click to Enter</button>
        </body>
        </html>"""
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": error_html
        }

# For local testing (optional)
if __name__ == "__main__":
    print("Run on Vercel - this is a serverless function")
