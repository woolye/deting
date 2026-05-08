def handler(request):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": """
        <!doctype html>
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
            font-family: Arial, sans-serif;
            overflow: hidden;
        }

        #enter {
            font-size: 28px;
            padding: 18px 40px;
            border: 2px solid white;
            color: white;
            background: transparent;
            cursor: pointer;
            letter-spacing: 2px;
            transition: all 0.4s ease;
        }

        #enter:hover {
            background: white;
            color: black;
            transform: scale(1.08);
        }

        #video {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            border: none;
            display: none;
            opacity: 0;
            transition: opacity 1.5s ease;
        }
        </style>
        </head>

        <body>

        <button id="enter">ENTER SITE</button>

        <iframe id="video"
            src="https://www.youtube.com/embed/2RWKJn8S9gg?autoplay=1&controls=0&rel=0"
            allow="autoplay; fullscreen"
            allowfullscreen>
        </iframe>

        <script>
        const btn = document.getElementById("enter");
        const video = document.getElementById("video");

        btn.addEventListener("click", () => {
            btn.style.opacity = "0";

            setTimeout(() => {
                btn.style.display = "none";
                video.style.display = "block";

                setTimeout(() => {
                    video.style.opacity = "1";
                }, 100);
            }, 400);
        });
        </script>

        </body>
        </html>
        """
    }
