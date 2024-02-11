import numpy as np
import cv2
#end goal
#get robot to move by itself and align nicly
#then work with the other 3 qr codes (ftc)


camera_id = 0
delay = 1
window_name = 'OpenCV QR Code'

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

                # Updated condition order
                if any(values[i][0] < 200 or values[i][0] > 500 or values[i][1] < 200 or values[i][1] > 500 for i in range(4)):
                    frame = cv2.putText(frame, "outside", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                elif any(300 < values[i][0] < 400 and 300 < values[i][1] < 400 for i in range(4)):
                    #move closer currently only checks if its inside that small box, so if its super far away but aligned perfectly, it will think its inside
                    #to be fixed
                    frame = cv2.putText(frame, "move closer", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    frame = cv2.putText(frame, "inside", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)


                frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
            
            frame = cv2.rectangle(frame, (200, 200), (500, 500), (0, 0, 255), 8)
            cv2.imshow(window_name, frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)
