from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)
camera_id = 0
delay = 1
corner1x=200
corner1y=200
corner2x=500
corner2y=500
targetcenterx=(corner1x+corner2x)/2
targetcentery=(corner1y+corner2y)/2
qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture(camera_id)
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)
def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = cap.read()  # read the camera frame
        if not success:
            break
        else:
            ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
            frame = cv2.rectangle(frame, (corner1x+50, corner1y+50), (corner2x-50, corner2y-50), (0, 0, 255), 8)
            frame = cv2.rectangle(frame, (corner1x, corner1y), (corner2x, corner2y), (0, 0, 255), 8)

            if ret_qr:
                for s, p in zip(decoded_info, points):
                    color = (0, 255, 0)
                    values = p.astype(int)
                    centerx = (int(values[0][0]) + int(values[1][0])) / 2
                    centery = (int(values[0][1]) + int(values[1][1])) / 2

                    if targetcenterx - centerx < 0:
                        text = "move left"
                    elif targetcenterx - centerx > 0:
                        text = "move right"
                    else:
                        text = "x value aligned"

                    frame = cv2.putText(frame, text, (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    if targetcentery < 0:
                        text = "move up"
                    elif targetcentery > 0:
                        text = "move down"
                    else:
                        text = "y value aligned"

                    frame = cv2.putText(frame, text, (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    frame = cv2.putText(frame, str(abs(targetcenterx - centerx)), (600, 100), cv2.FONT_HERSHEY_SIMPLEX,
                                        1, (0, 0, 255), 2, cv2.LINE_AA)
                    frame = cv2.putText(frame, str(abs(targetcentery - centery)), (600, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                        1, (0, 0, 255), 2, cv2.LINE_AA)

                    if any(values[i][0] < corner1x or values[i][0] > corner2x or values[i][1] < corner1y or
                           values[i][1] > corner2y for i in range(4)):
                        text = "outside"
                    elif not any(
                            corner2x - 50 > values[i][0] > corner1x + 50 and corner2y - 50 > values[i][1] > corner1y + 50
                            for i in range(4)):
                        text = "aligned"
                    else:
                        text = "inside"

                    frame = cv2.putText(frame, text, (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
            else:
                frame = cv2.putText(frame, "qr code not detected", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                    2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)