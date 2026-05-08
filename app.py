# app.py - Flask application that logs visitor IP addresses and serves the video entry page
# Deploy this on Vercel with the provided vercel.json configuration

from flask import Flask, request, render_template_string
import datetime
import os

app = Flask(__name__)

# Path for the log file (writable in Vercel's /tmp directory)
LOG_FILE = '/tmp/visitor_ips.log'

def log_ip_address(ip, user_agent=None, path='/'):
    """Log the visitor's IP address with timestamp and optional user agent"""
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] IP: {ip} | Path: {path} | UA: {user_agent or 'N/A'}\n"
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        # Also print to console for Vercel logs (visible in deployment dashboard)
        print(log_entry.strip())
        
        return True
    except Exception as e:
        print(f"Error logging IP: {e}")
        return False

def get_visitor_ip():
    """Extract real IP address from request (handles proxies and Vercel forwarding)"""
    # Check for forwarded headers (Vercel, nginx, etc.)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2)
        # The first one is the original client IP
        ip = forwarded_for.split(',')[0].strip()
        return ip
    
    # Check for Cloudflare or other CDN headers
    cf_connecting_ip = request.headers.get('CF-Connecting-IP')
    if cf_connecting_ip:
        return cf_connecting_ip
    
    # Check for Vercel specific header
    vercel_forwarded = request.headers.get('x-vercel-forwarded-for')
    if vercel_forwarded:
        return vercel_forwarded.split(',')[0].strip()
    
    # Fallback to direct remote address
    return request.remote_addr or '0.0.0.0'

# HTML template for the video entry page
VIDEO_PAGE_TEMPLATE = '''
<!DOCTYPE html>
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

        /* ENTRY MODAL / BUTTON CONTAINER */
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

        /* premium enter button */
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

        /* ip console / log display */
        .ip-console {
            position: fixed;
            bottom: 18px;
            right: 20px;
            background: rgba(0, 0, 0, 0.7);
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

        /* fullscreen iframe */
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

        /* small loading indicator while prepping */
        .status-text {
            color: rgba(255,255,255,0.6);
            font-size: 0.75rem;
            text-align: center;
            font-family: monospace;
        }
    </style>
</head>
<body>

    <!-- ENTRY LAYER -->
    <div class="entry-container" id="entryContainer">
        <button class="enter-button" id="enterBtn">ENTER SITE</button>
        <div class="status-text" id="statusMsg">✨ ready</div>
    </div>

    <!-- YOUTUBE IFRAME (autoplay, controls hidden) -->
    <iframe id="videoFrame" class="video-frame"
        src="https://www.youtube.com/embed/2RWKJn8S9gg?enablejsapi=1&autoplay=0&controls=0&rel=0&mute=0&modestbranding=1"
        allow="autoplay; fullscreen; accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
    </iframe>

    <!-- IP CONSOLE (displays the logged IP address) -->
    <div class="ip-console" id="ipConsole">
        📡 IP LOG: <span id="ipValue">collecting...</span>
    </div>

    <script>
        // Get DOM elements
        const entryContainer = document.getElementById('entryContainer');
        const enterBtn = document.getElementById('enterBtn');
        const videoFrame = document.getElementById('videoFrame');
        const ipValueSpan = document.getElementById('ipValue');
        const statusMsg = document.getElementById('statusMsg');

        // Store the viewer's IP (received from backend)
        let viewerIP = '{{ visitor_ip }}';

        // Display the IP in the console right away
        if (viewerIP && viewerIP !== '') {
            ipValueSpan.textContent = viewerIP;
            statusMsg.textContent = '✓ IP logged | click to enter';
        } else {
            ipValueSpan.textContent = 'awaiting';
            statusMsg.textContent = 'initializing...';
        }

        // Function to start video playback with autoplay enabled
        function startVideo() {
            // Modify the iframe src to add autoplay=1 (ensures video starts playing)
            const currentSrc = videoFrame.src;
            if (!currentSrc.includes('autoplay=1')) {
                // Add autoplay parameter, preserve other params
                let newSrc = currentSrc.replace('autoplay=0', 'autoplay=1');
                if (newSrc === currentSrc) {
                    // fallback: if autoplay=0 not found, just append &autoplay=1
                    newSrc = currentSrc + (currentSrc.includes('?') ? '&autoplay=1' : '?autoplay=1');
                }
                videoFrame.src = newSrc;
            } else {
                // reload to trigger autoplay
                videoFrame.src = videoFrame.src;
            }
            
            // Make iframe visible
            videoFrame.style.display = 'block';
            
            // Optional: request fullscreen for deeper immersion (user-initiated)
            try {
                if (videoFrame.requestFullscreen) {
                    videoFrame.requestFullscreen().catch(e => console.log('fullscreen not allowed', e));
                }
            } catch(e) { console.log(e); }
        }

        // Handler for ENTER button click
        enterBtn.onclick = () => {
            // Fade out the entry container (button + status)
            entryContainer.classList.add('fade-out');
            
            // Slight delay to let CSS transition happen, then start video
            setTimeout(() => {
                startVideo();
                // optional: log to console that user entered
                console.log('User entered the experience. IP:', viewerIP);
            }, 200);
        };

        // Preload / warmup: ensure that iframe is ready but not autoplaying yet
        // (this improves playback speed when clicking)
        window.addEventListener('load', () => {
            // small delay just to show the ip is confirmed
            if (viewerIP && viewerIP !== '') {
                statusMsg.textContent = '✓ ready — click ENTER';
            } else {
                // fallback: fetch IP from a public API if server-side variable failed
                fetch('https://api.ipify.org?format=json')
                    .then(res => res.json())
                    .then(data => {
                        if (data.ip && (!viewerIP || viewerIP === '' || viewerIP === '0.0.0.0')) {
                            viewerIP = data.ip;
                            ipValueSpan.textContent = viewerIP;
                            statusMsg.textContent = '✓ IP resolved | ready';
                        }
                    })
                    .catch(err => console.warn('ip fallback error', err));
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main route: logs visitor IP and serves the video entry page"""
    # Extract real IP address (handles proxies, Vercel forwarding)
    visitor_ip = get_visitor_ip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Log the IP address to file system and console
    log_ip_address(visitor_ip, user_agent, '/')
    
    # Render the HTML template with the visitor's IP embedded
    return render_template_string(VIDEO_PAGE_TEMPLATE, visitor_ip=visitor_ip)

@app.route('/health')
def health():
    """Health check endpoint for Vercel monitoring"""
    return {'status': 'ok', 'message': 'IP logging active'}, 200

@app.route('/logs')
def view_logs():
    """Optional endpoint to view recent logs (for debugging, but IPs are sensitive)"""
    # In production you might want to protect this route
    # This is just for testing to confirm IP logging works
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                # Return last 20 lines
                recent = lines[-20:] if len(lines) > 20 else lines
                return '<pre>' + '\n'.join(recent) + '</pre>'
        else:
            return '<pre>No logs yet.</pre>'
    except Exception as e:
        return f'<pre>Error reading logs: {e}</pre>'

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
