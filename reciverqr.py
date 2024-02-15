import numpy as np
import cv2
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import signal
import sys
import os

# Global variables
corner1x = 200
corner1y = 200
corner2x = 500
corner2y = 500
targetcenterx = (corner1x + corner2x) / 2
targetcentery = (corner1y + corner2y) / 2
qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture(0)
delay = 1
window_name = 'OpenCV QR Code'

# Flask setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])
xTriggered = 0  # Declare xTriggered globally

@app.route('/')
def index():
    return """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>input</title>
    </head>
    <body>
        <h1>input</h1>
        <form id="dataForm">
            <fieldset>
                <label for="target">type to initialize:</label>
                <input id="target" type="text" style="color: transparent; text-shadow: 0 0 0 #0000;">
            </fieldset>
        </form>
        <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
        <script>
            var xTriggered = 0;
            $("#target").on("keydown", function (event) {
                if (event.which == 13) {
                    event.preventDefault();
                }
                xTriggered++;
                var pressedKey = String.fromCharCode(event.which);
                var msg = "Handler for `keydown` called " + xTriggered + " time(s). Pressed Key: " + pressedKey;
                console.log(msg);
                console.log(event);

                $.ajax({
                    type: 'POST',
                    contentType: 'application/json;charset=UTF-8',
                    data: JSON.stringify({'xTriggered': xTriggered, 'pressedKey': pressedKey}),
                    dataType: 'json',
                    url: '/process_data',
                    success: function (data) {
                        console.log('Server Response:', data);
                    }
                });
            });
        </script>
    </body>
    </html>
    """

@app.route('/process_data', methods=['POST'])
def process_data():
    global corner1x, corner2x, corner1y, corner2y, xTriggered
    data = request.get_json()

    if not data or 'xTriggered' not in data or 'pressedKey' not in data:
        return jsonify({'error': 'Invalid data format'})

    xTriggered = data.get('xTriggered', 0)
    pressedKey = data.get('pressedKey', '')

    if pressedKey.lower() == "a":
        print("left")
        corner1x -= 50
        corner2x -= 50
    if pressedKey.lower() == "s":
        print("backward")
        corner1y += 50
        corner2y += 50
    if pressedKey.lower() == "w":
        print("forward")
        corner1y -= 50
        corner2y -= 50
    if pressedKey.lower() == "d":
        print("right")
        corner1x += 50
        corner2x += 50
    if pressedKey.lower() == "q":
        print("autonomous")
    if pressedKey.lower() == "e":
        print("stopping motors")
    
    print(f'xTriggered: {xTriggered}, Pressed Key: {pressedKey}')

    response_data = {'message': f'Data processed successfully! xTriggered: {xTriggered}, Pressed Key: {pressedKey}'}
    print(response_data)
    return jsonify(response_data)

def process_qr(frame):
    global corner1x, corner2x, corner1y, corner2y, targetcenterx, targetcentery

    ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
    
    if ret_qr:
        for s, p in zip(decoded_info, points):
            color = (0, 255, 0)
            values = p.astype(int)
            centerx = (int(values[0][0]) + int(values[1][0])) / 2
            centery = (int(values[0][1]) + int(values[1][1])) / 2

            if targetcenterx - centerx < 0:
                frame = cv2.putText(frame, "move left", (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            elif targetcenterx - centerx > 0:
                frame = cv2.putText(frame, "move right", (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                frame = cv2.putText(frame, "x value aligned", (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            
            if targetcentery < 0:
                frame = cv2.putText(frame, "move up", (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            elif targetcentery > 0:
                frame = cv2.putText(frame, "move down", (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                frame = cv2.putText(frame, "y value aligned", (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            frame = cv2.putText(frame, str(abs(targetcenterx - centerx)), (600, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            frame = cv2.putText(frame, str(abs(targetcentery - centery)), (600, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            
            if any(values[i][0] < corner1x or values[i][0] > corner2x or values[i][1] < corner1y or values[i][1] > corner2y for i in range(4)):
                frame = cv2.putText(frame, "outside", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            elif not any(corner2x - 50 > values[i][0] > corner1x + 50 and corner2y - 50 > values[i][1] > corner1y + 50 for i in range(4)):
                frame = cv2.putText(frame, "aligned", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                frame = cv2.putText(frame, "inside", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
    else:
        frame = cv2.putText(frame, "qr code not detected", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    frame = cv2.rectangle(frame, (corner1x + 50, corner1y + 50), (corner2x - 50, corner2y - 50), (0, 0, 255), 8)
    frame = cv2.rectangle(frame, (corner1x, corner1y), (corner2x, corner2y), (0, 0, 255), 8)

    return frame

def opencv_loop():
    global cap, window_name

    while True:
        ret, frame = cap.read()

        if ret:
            frame = process_qr(frame)

            cv2.imshow(window_name, frame)

            if cv2.waitKey(delay) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

def signal_handler(signal, frame):
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)

if __name__ == '__main__':
    # Start OpenCV loop in a separate thread
    opencv_thread = threading.Thread(target=opencv_loop)
    opencv_thread.start()

    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)

    # Start Flask app in the main thread
    app.run(host='0.0.0.0', debug=True)
