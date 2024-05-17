from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# Message queue for video frames
frame_queue = []

# Endpoint for video streaming devices
@socketio.on('stream_video')
def handle_stream(frame_data):
    frame_queue.append(frame_data)

# Endpoint for viewers
@socketio.on('view_video')
def handle_view():
    while True:
        if frame_queue:
            frame = frame_queue.pop(0)
            socketio.emit('video_frame', frame)

if __name__ == '__main__':
    socketio.run(app)
