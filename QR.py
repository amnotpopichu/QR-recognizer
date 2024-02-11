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
                print(p.astype(int)[1][1])
                print("\n")
                

                frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
        frame = cv2.rectangle(frame,(200,200),(500,500),(0,0,255),8)
        cv2.imshow(window_name, frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)