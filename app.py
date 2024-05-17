from flask import Flask, Response, render_template
import subprocess
import threading

app = Flask(__name__)

# RTMP Configuration (Adjust as needed)
RTMP_INPUT = "rtmp://localhost/live/drone"  # Where drone sends video
RTMP_OUTPUT = "rtmp://localhost/live/stream" # Where clients receive

# FFmpeg Process (Handles RTMP transcoding)
ffmpeg_process = None

def start_ffmpeg():
    global ffmpeg_process
    ffmpeg_command = [
        "ffmpeg",
        "-i", RTMP_INPUT,
        "-c:v", "copy",  # Efficient video stream copying
        "-f", "flv",     # FLV format for browser compatibility
        RTMP_OUTPUT
    ]
    ffmpeg_process = subprocess.Popen(ffmpeg_command)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def generate():
        # Start FFmpeg if not running
        if ffmpeg_process is None or ffmpeg_process.poll() is not None:
            start_ffmpeg()

        # Use FFmpeg to read from RTMP_OUTPUT and yield chunks
        with subprocess.Popen(["ffmpeg", "-i", RTMP_OUTPUT, "-f", "mpegts", "-"], 
                              stdout=subprocess.PIPE) as proc:
            while True:
                data = proc.stdout.read(1024)
                if not data:
                    break
                yield data

    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)  # Threaded for multiple clients