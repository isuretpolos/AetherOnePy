# server.py
from flask import Flask, Response
from flask_socketio import SocketIO
import cv2

app = Flask(__name__)
socketio = SocketIO(app)

def generate_video():
    cap = cv2.VideoCapture(0)  # Capture video from webcam
    while True:
        success, frame = cap.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
