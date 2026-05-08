# app.py - Optimized video player with real IP logging

from datetime import datetime
import json

# HTML page with optimized video loading and faster playback
HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ENTER SITE</title>
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
            z-index: 20;
            position: relative;
        }
        #enter:hover {
            background: white;
            color: black;
            transform: scale(1.1);
        }
        #video-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            display: none;
            z-index: 10;
            background: black;
        }
        #youtube-video {
            width: 100%;
            height: 100%;
            border: none;
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
        .loading {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            display: none;
            z-index: 30;
        }
    </style>
</head>
<body>
    <button id="enter">ENTER SITE</button>
    <div id="video-container">
        <iframe id="youtube-video" src="https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=0&controls=0&rel=0&enablejsapi=1" allow="autoplay; fullscreen"></iframe>
    </div>
    <div id="ip-log">🌐 IP: <span id="ip-addr">{{IP}}</span></div>
    <div class="loading" id="loading">Loading video...</div>
    
    <script>
        let visitorIP = "{{IP}}";
        let playerReady = false;
        
        // Display IP
        if (visitorIP && visitorIP !== "") {
            document.getElementById("ip-addr").innerText = visitorIP;
        }
        
        // Preload video in background
        const videoContainer = document.getElementById('video-container');
        const videoFrame = document.getElementById('youtube-video');
        const enterBtn = document.getElementById('enter');
        const loadingDiv = document.getElementById('loading');
        
        // Preload video quietly in background
        let preloadAttempted = false;
        
        function preloadVideo() {
            if (preloadAttempted) return;
            preloadAttempted = true;
            
            // Preload with mute to allow autoplay later
            const preloadSrc = "https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=0&controls=0&rel=0&mute=1&enablejsapi=1";
            videoFrame.src = preloadSrc;
        }
        
        // Start preloading immediately
        preloadVideo();
        
        // Enter button click
        enterBtn.onclick = () => {
            enterBtn.style.display = "none";
            loadingDiv.style.display = "block";
            videoContainer.style.display = "block";
            
            // Force reload with autoplay
            const finalSrc = "https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=1&controls=0&rel=0&mute=0&enablejsapi=1";
            videoFrame.src = finalSrc;
            
            // Hide loading after video starts (estimated)
            setTimeout(() => {
                loadingDiv.style.display = "none";
            }, 1000);
            
            // Try fullscreen
            try {
                videoContainer.requestFullscreen();
            } catch(e) {}
        };
    </script>
</body>
</html>"""

def log_ip_to_vercel(ip, ua=""):
    """Log IP to Vercel function logs (where you can see real IPs)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # This prints to Vercel FUNCTION logs (not access logs)
    print(f"=== VISITOR DETECTED ===")
    print(f"Time: {timestamp}")
    print(f"IP Address: {ip}")
    print(f"User Agent: {ua[:100]}")
    print(f"=========================")
    
    # Also save to temp file
    try:
        with open("/tmp/visitors.log", "a") as f:
            f.write(f"[{timestamp}] IP: {ip} | UA: {ua}\n")
    except:
        pass
    
    return True

def get_real_ip(environ, headers):
    """Extract real visitor IP from Vercel headers"""
    
    # Print all headers for debugging (appears in Vercel logs)
    print("Debug - Checking headers for real IP...")
    
    # Try each possible header (Vercel specific)
    possible_headers = [
        ('x-vercel-forwarded-for', headers.get('x-vercel-forwarded-for', '')),
        ('x-forwarded-for', headers.get('x-forwarded-for', '')),
        ('x-real-ip', headers.get('x-real-ip', '')),
        ('cf-connecting-ip', headers.get('cf-connecting-ip', '')),
        ('true-client-ip', headers.get('true-client-ip', ''))
    ]
    
    for header_name, header_value in possible_headers:
        if header_value:
            # Get first IP if multiple
            ip = header_value.split(',')[0].strip()
            if ip and ip != '127.0.0.1' and ip != '::1':
                print(f"Found real IP from {header_name}: {ip}")
                return ip
    
    # Fallback to remote addr
    remote_addr = environ.get('REMOTE_ADDR', '')
    if remote_addr and remote_addr != '127.0.0.1':
        return remote_addr
    
    return 'Unable to detect (check function logs)'

def app(environ, start_response):
    """Main Vercel app function"""
    
    try:
        # Parse headers from environment
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').lower()
                headers[header_name] = value
        
        # Get user agent
        user_agent = headers.get('user-agent', 'Unknown')
        
        # Get real IP address
        real_ip = get_real_ip(environ, headers)
        
        # Log the IP (appears in Vercel function logs)
        log_ip_to_vercel(real_ip, user_agent)
        
        # Create HTML with IP
        html = HTML_PAGE.replace("{{IP}}", real_ip)
        
        # Send response
        status = '200 OK'
        response_headers = [
            ('Content-Type', 'text/html'),
            ('Cache-Control', 'public, max-age=3600'),  # Cache for faster loading
            ('Content-Length', str(len(html)))
        ]
        start_response(status, response_headers)
        return [html.encode('utf-8')]
        
    except Exception as e:
        # Simple error page
        error_html = f"""<!DOCTYPE html>
        <html>
        <body style="background:black;color:white;text-align:center;padding-top:50px">
            <h1>Site is live!</h1>
            <button onclick="location.reload()" style="padding:15px 30px">Enter Site</button>
            <div style="position:fixed;bottom:10px;right:10px;color:#0f0">IP: Visitor</div>
        </body>
        </html>"""
        
        status = '200 OK'
        response_headers = [('Content-Type', 'text/html')]
        start_response(status, response_headers)
        return [error_html.encode('utf-8')]
