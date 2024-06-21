html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Live Stream</title>
    </head>
    <body>
        <h1>Live Stream</h1>
        <div id="videos">
        </div>
        <script>
            const cameraCount = 5;  // 修改為攝影機數量
            for (let i = 0; i < cameraCount; i++) {
                const img = document.createElement('img');
                img.id = 'live-image-' + i;
                img.src = '';
                img.width = 640;
                img.height = 480;
                document.getElementById('videos').appendChild(img);
                const ws = new WebSocket('ws://localhost:8001/live/ws/' + i);
                ws.onopen = function(event) {
                    console.log(`WebSocket connection for camera ${i} is open.`);
                    // 連線成功的處理邏輯，例如顯示連線狀態
                    const statusElement = document.createElement('div');
                    statusElement.id = 'status-' + i;
                    statusElement.innerText = `Camera ${i}: Connected`;
                    document.body.appendChild(statusElement);
                };

                ws.onmessage = function(event) {
                    const imgElement = document.getElementById('live-image-' + i);
                    imgElement.src = 'data:image/jpeg;base64,' + event.data;
                };

                ws.onerror = function(event) {
                    console.error(`WebSocket error for camera ${i}:`, event);
                    // 錯誤處理邏輯，例如顯示錯誤狀態
                    const statusElement = document.getElementById('status-' + i);
                    statusElement.innerText = `Camera ${i}: Error`;
                };

                ws.onclose = function(event) {
                    console.log(`WebSocket connection for camera ${i} is closed.`);
                    // 連線關閉的處理邏輯，例如顯示斷開狀態
                    const statusElement = document.getElementById('status-' + i);
                    statusElement.innerText = `Camera ${i}: Disconnected`;
                };
            }
        </script>
    </body>
</html>
"""

hls_html = """
<!DOCTYPE html>
<html>
<head>
    <title>HLS Stream</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
</head>
<body>
    <h1>HLS Stream</h1>
    <video id="video" controls></video>
    <script>
        var video = document.getElementById('video');
        video.width = 640;
        video.height = 480;
        if(Hls.isSupported()) {
            var hls = new Hls();
            hls.loadSource('/live/hls/0/camera_0.m3u8');
            hls.attachMedia(video);
            hls.on(Hls.Events.MANIFEST_PARSED, function() {
                video.play();
            });
        }
        else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = '/live/hls/0/camera_0.m3u8';
            video.addEventListener('loadedmetadata', function() {
                video.play();
            });
        }
    </script>
</body>
</html>
"""