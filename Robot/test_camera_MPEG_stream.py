#!/usr/bin/python3

# This is the same as mjpeg_server.py, but uses the h/w MJPEG encoder.

import io
import logging
import socketserver
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
from libcamera import Transform

PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BASARNAS Control Panel</title>
<style>
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  
  .header {
    width: 100%;
    background-color: #004225; /* Darker green for contrast */
    color: white;
    padding: 0.5rem 0;
    text-align: center;
  }

  .logo {
    height: 65px; /* Sesuaikan dengan ukuran logo BASARNAS */
  }

  .main-content {
    display: flex;
    flex-direction: center;
    justify-content: center;
    align-items: center; /* Align items to the start to prevent vertical stretching */
    margin-top: 10px; /* Added margin to the top */
  }

  .video-stream {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    margin-right: 20px;
  }

  #webcam {
    width: 640px;
    height: 480px;
    border-radius: 8px;
  }

  .controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
    margin-top: 30px; /* Increase margin-top to move the buttons down */
  }

  .control-button {
    padding: 10px 30px;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.3s ease;
    color: white;
  }

  .stop-button {
    background-color: #bf2f2f;
  }

  .continue-button {
    background-color: #4caf50;
  }

  .camera-control-button {
    padding: 10px 20px;
    border: none;
    border-radius: 20px; /* Rounded corners for the buttons */
    cursor: pointer;
    font-weight: bold;
    color: white;
    background-color: #6c757d; /* Neutral color for camera controls */
    margin-top: 10px; /* Margin to separate the camera controls from movement controls */
    width: 200px; /* Fixed width for consistency */
  }

  .camera-control-button:hover {
    background-color: #5a6268; /* Slightly darker on hover for feedback */
  }

  .camera-controls {
    display: flex; /* This will align the camera control buttons horizontally */
    justify-content: space-between; /* This will place the buttons on opposite ends */
    width: 100%; /* Set the width to the parent container's width */
  }

  .notification {
    color: #31708f;
    background-color: #d9edf7;
    border-color: #bce8f1;
    padding: 10px;
    border-radius: 4px;
    margin-top: 10px; /* Move notification below the video stream */
    margin-right: 400px;
    display: none;
    
  }

</style>
</head>
<body>
<header class="header">
  <img src="Basarnas_Logo.png" alt="BASARNAS Logo" class="logo">
  <h1>BASARNAS CONTROL PANEL</h1>
</header>

<div class="main-content">
  <div class="video-stream">
    <img  src="stream.mjpg" width="640" height="480" />
  </div>

  <div class="controls">
    <button class="control-button stop-button" onclick="stopRobot()">Stop Movement</button>
    <button class="control-button continue-button" onclick="continueRobot()">Continue Movement</button>
   
    <div class="camera-controls">
      <button class="camera-control-button" onclick="turnCamera('left')">Camera Turn Left</button>
      <button class="camera-control-button" onclick="turnCamera('right')">Camera Turn Right</button>
    </div>
  </div>
</div>

<div class="notification" id="notification"></div>

<script>
  function stopRobot() {
    document.getElementById('notification').textContent = 'Robot Has Been Stopped';
    document.getElementById('notification').style.display = 'block';
  }

  function continueRobot() {
    document.getElementById('notification').textContent = 'Robot is Continuing Movement';
    document.getElementById('notification').style.display = 'block';
  }

  function turnCamera(direction) {
    // Logika untuk memutar kamera ke kiri atau kanan
    console.log(`Camera Turning ${direction}`);
    // Hilangkan alert dan ganti dengan log atau lainnya sesuai kebutuhan
  }

  function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.style.display = 'block';
  }

  const videoElement = document.getElementById('webcam');
  if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function (stream) {
        videoElement.srcObject = stream;
      })
      .catch(function (err) {
        console.log("Something went wrong!", err);
      });
  }
</script>

</body>
</html>


"""




class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(transform=Transform(vflip=True),main={"size": (640, 480)}))
output = StreamingOutput()
picam2.start_recording(MJPEGEncoder(), FileOutput(output))

try:
    address = ('192.168.146.222', 8888)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    picam2.stop_recording()