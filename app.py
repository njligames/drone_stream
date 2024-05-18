from flask import Flask, request, Response, render_template_string
from queue import Queue
import threading
import cv2
import marshal

app = Flask(__name__)

# Shared queue to store frames from video streaming devices and webcam
frame_queue = Queue(maxsize=10)

# def capture_frames():
#     """Capture frames from the system webcam and put them in the queue"""
#     cap = cv2.VideoCapture(0)
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         _, buffer = cv2.imencode('.jpg', frame)
#         if frame_queue.full():
#             frame_queue.get()  # Remove the oldest frame if the queue is full
#         frame_queue.put(buffer.tobytes())
#     cap.release()
#
# # Start capturing frames from the webcam in a background thread
# threading.Thread(target=capture_frames, daemon=True).start()

@app.route('/stream', methods=['POST'])
def stream():
    """Endpoint for video streaming devices to send frames"""
    # frame = marshal.loads(request.data)['data']
    frame = request.data
    if frame_queue.full():
        frame_queue.get()  # Remove the oldest frame if the queue is full
    frame_queue.put(frame)
    return 'Frame received', 200

@app.route('/view')
def view():
    """Endpoint for clients to view the video stream"""
    def generate():
        while True:
            frame = frame_queue.get()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Simple HTML page to view the video stream"""
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Webcam Streaming</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.js"></script>
            <script>
                var socket = io();
                socket.on('message', function(msg) {
                    console.log(msg);
                });
            </script>
        </head>
        <body>
            <h1>Webcam Stream</h1>
            <img src="{{ url_for('view') }}" width="640" height="480">
        </body>
        </html>

    ''')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5001)
