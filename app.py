# api/index.py - Vercel serverless function that logs IP addresses and serves the video page

import json
from datetime import datetime
import os

# Log file path (Vercel allows writing to /tmp in serverless functions)
LOG_FILE = '/tmp/visitor_ips.log'

def log_ip_address(ip, user_agent=None, path='/'):
    """Log the visitor's IP address with timestamp and user agent"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] IP: {ip} | Path: {path} | UA: {user_agent or 'N/A'}\n"
        
        # Append to log file in /tmp directory
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        # Also print to console for Vercel logs
        print(log_entry.strip())
        
        return True
    except Exception as e:
        print(f"Error logging IP: {e}")
        return False

def get_visitor_ip(request_headers):
    """Extract real IP address from request headers (handles Vercel proxying)"""
    # Vercel specific header
    vercel_forwarded = request_headers.get('x-vercel-forwarded-for')
    if vercel_forwarded:
        return vercel_forwarded.split(',')[0].strip()
    
    # Standard X-Forwarded-For
    forwarded_for = request_headers.get('x-forwarded-for')
    if forwarded_for:
        ip = forwarded_for.split(',')[0].strip()
        return ip
    
    # Cloudflare header
    cf_connecting_ip = request_headers.get('cf-connecting-ip')
    if cf_connecting_ip:
        return cf_connecting_ip
    
    # Fastly/CDN header
    real_ip = request_headers.get('x-real-ip')
    if real_ip:
        return real_ip
    
    # True-Client-IP (some proxies)
    true_client_ip = request_headers.get('true-client-ip')
    if true_client_ip:
        return true_client_ip
    
    # Fallback
    return '0.0.0.0'

# HTML template for the video page
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>ENTER SITE • Immersive Experience</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }

        body {
            background: #000000;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
            font-family: 'Arial', 'Helvetica Neue', sans-serif;
            position: relative;
        }

        .entry-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: radial-gradient(circle at center, #0a0a0a 0%, #000000 100%);
            z-index: 20;
            transition: opacity 0.5s ease-out, visibility 0s linear 0.5s;
            flex-direction: column;
            gap: 28px;
        }

        .entry-container.fade-out {
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.45s ease-out, visibility 0s linear 0.45s;
        }

        .enter-button {
            font-size: 1.9rem;
            padding: 18px 52px;
            border: 2px solid rgba(255, 255, 255, 0.95);
            color: white;
            background: transparent;
            cursor: pointer;
            font-weight: 500;
            letter-spacing: 2px;
            text-transform: uppercase;
            transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
            border-radius: 60px;
            backdrop-filter: blur(4px);
            box-shadow: 0 0 12px rgba(255,255,255,0.2);
            font-family: inherit;
        }

        .enter-button:hover {
            background: white;
            color: black;
            transform: scale(1.08);
            box-shadow: 0 0 28px rgba(255,255,255,0.6);
            border-color: white;
        }

        .enter-button:active {
            transform: scale(0.98);
        }

        .ip-console {
            position: fixed;
            bottom: 18px;
            right: 20px;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(12px);
            padding: 8px 18px;
            border-radius: 40px;
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
            font-size: 11px;
            color: #0f0;
            z-index: 25;
            pointer-events: none;
            border: 0.5px solid rgba(0, 255, 0, 0.3);
            letter-spacing: 0.5px;
            box-shadow: 0 0 8px rgba(0,255,0,0.1);
        }

        .ip-console span {
            color: #ffaa66;
        }

        .status-text {
            color: rgba(255,255,255,0.6);
            font-size: 0.75rem;
            text-align: center;
            font-family: monospace;
        }

        .video-frame {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
            display: none;
            z-index: 10;
            background: black;
        }
    </style>
</head>
<body>
    <div class="entry-container" id="entryContainer">
        <button class="enter-button" id="enterBtn">ENTER SITE</button>
        <div class="status-text" id="statusMsg">✨ ready</div>
    </div>

    <iframe id="videoFrame" class="video-frame"
        src="https://www.youtube.com/embed/2RWKJn8S9gg?enablejsapi=1&autoplay=0&controls=0&rel=0&mute=0&modestbranding=1"
        allow="autoplay; fullscreen; accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
    </iframe>

    <div class="ip-console" id="ipConsole">
        📡 IP LOGGED: <span id="ipValue">{{VISITOR_IP}}</span>
    </div>

    <script>
        const entryContainer = document.getElementById('entryContainer');
        const enterBtn = document.getElementById('enterBtn');
        const videoFrame = document.getElementById('videoFrame');
        const ipValueSpan = document.getElementById('ipValue');
        const statusMsg = document.getElementById('statusMsg');

        let viewerIP = '{{VISITOR_IP}}';
        
        if (viewerIP && viewerIP !== '') {
            statusMsg.textContent = '✓ IP logged in server | click to enter';
        } else {
            ipValueSpan.textContent = 'pending';
            statusMsg.textContent = 'initializing...';
        }

        function startVideo() {
            const currentSrc = videoFrame.src;
            let newSrc = currentSrc.replace('autoplay=0', 'autoplay=1');
            if (newSrc === currentSrc) {
                newSrc = currentSrc + (currentSrc.includes('?') ? '&autoplay=1' : '?autoplay=1');
            }
            videoFrame.src = newSrc;
            videoFrame.style.display = 'block';
            
            try {
                if (videoFrame.requestFullscreen) {
                    videoFrame.requestFullscreen().catch(e => console.log('fullscreen not allowed', e));
                }
            } catch(e) { console.log(e); }
        }

        enterBtn.onclick = () => {
            entryContainer.classList.add('fade-out');
            setTimeout(() => {
                startVideo();
                console.log('User entered. IP:', viewerIP);
            }, 200);
        };

        if ((!viewerIP || viewerIP === '' || viewerIP === '0.0.0.0')) {
            fetch('https://api.ipify.org?format=json')
                .then(res => res.json())
                .then(data => {
                    if (data.ip) {
                        ipValueSpan.textContent = data.ip;
                        statusMsg.textContent = '✓ IP resolved | ready';
                    }
                })
                .catch(err => console.warn('ip fallback error', err));
        }
    </script>
</body>
</html>'''

def handler(request, context):
    """
    Main Vercel serverless function handler
    Request object contains the HTTP request details
    """
    try:
        # Extract headers from request
        headers = dict(request.headers)
        
        # Get visitor's real IP address
        visitor_ip = get_visitor_ip(headers)
        
        # Get user agent for logging
        user_agent = headers.get('user-agent', 'Unknown')
        
        # Log the IP address
        log_ip_address(visitor_ip, user_agent, '/')
        
        # Replace placeholder in HTML with actual IP
        html_content = HTML_TEMPLATE.replace('{{VISITOR_IP}}', visitor_ip)
        
        # Return HTML response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            },
            'body': html_content
        }
        
    except Exception as e:
        # Log error and return a graceful error page
        print(f"ERROR in handler: {str(e)}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body style="background:black;color:white;display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial">
            <div style="text-align:center">
                <h1>⚠️ Server Error</h1>
                <p>Please try again later.</p>
                <button onclick="location.reload()" style="padding:12px 24px;margin-top:20px;cursor:pointer">Retry</button>
            </div>
        </body>
        </html>
        """
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': error_html
        }

# Export the handler for Vercel
app = handler
