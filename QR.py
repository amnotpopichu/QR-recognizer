import cv2

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
                #0,0 gives x of verticy 1
                #remeber your ranges and it starrts at 0 lol
                values = p.astype(int)
                if all(200 < values[i][j] < 500 for i in range(4) for j in range(2)):
                    frame = cv2.putText(frame, "inside", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                else:
                    frame = cv2.putText(frame, "outside", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                

                frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
        frame = cv2.rectangle(frame,(200,200),(500,500),(0,0,255),8)
        cv2.imshow(window_name, frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)