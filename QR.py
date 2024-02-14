#Calibration- use center to align but when autonomous must disable and 
#override other commands otherwise error doesn’t register, use centers, minus
# need move right, positive need move left. Align inside function SHOULD NOT take president over center aligning.


import numpy as np
import cv2
#end goal
#get robot to move by itself and align nicly
#then work with the other 3 qr codes (ftc)
#get code to work with a wheel
#https://note.nkmk.me/en/python-opencv-qrcode/
camera_id = 0
delay = 1
window_name = 'OpenCV QR Code'
corner1x=200
corner1y=200
corner2x=500
corner2y=500
targetcenterx=(corner1x+corner2x)/2
targetcentery=(corner1y+corner2y)/2
qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture(camera_id)
while True:
    ret, frame = cap.read()

    if ret:
        ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
        if ret_qr:
            for s, p in zip(decoded_info, points):
                color = (0, 255, 0)
                values = p.astype(int)
                centerx = (int(values[0][0])+int(values[1][0]))/2
                centery = (int(values[0][1])+int(values[1][1]))/2
                if targetcenterx-centerx<0:
                    frame = cv2.putText(frame, "move left", (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                elif targetcenterx-centerx>0:
                    frame = cv2.putText(frame, "move right", (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    frame = cv2.putText(frame, "x value aligned", (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                if targetcentery-centery < 0:
                        text = "move up"
                elif targetcentery-centery > 0:
                    text = "move down"
                else:
                    frame = cv2.putText(frame, "y value aligned", (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                frame = cv2.putText(frame, str(abs(targetcenterx-centerx)), (600, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                frame = cv2.putText(frame, str(abs(targetcentery-centery)), (600, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                # Updated condition order
                if any(values[i][0] < corner1x or values[i][0] > corner2x or values[i][1] < corner1y or values[i][1] > corner2y for i in range(4)):
                    frame = cv2.putText(frame, "outside", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                elif not any(corner2x-50>values[i][0] > corner1x+50 and corner2y-50>values[i][1] > corner1y+50 for i in range(4)):
                    frame = cv2.putText(frame, "aligned", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                else:
                    frame = cv2.putText(frame, "inside", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)


                frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
        else:
            frame = cv2.putText(frame, "qr code not detected", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
    frame = cv2.rectangle(frame, (corner1x+50, corner1y+50), (corner2x-50, corner2y-50), (0, 0, 255), 8)

    frame = cv2.rectangle(frame, (corner1x, corner1y), (corner2x, corner2y), (0, 0, 255), 8)

    cv2.imshow(window_name, frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)
