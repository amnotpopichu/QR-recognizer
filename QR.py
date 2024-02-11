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
                #https://note.nkmk.me/en/python-opencv-qrcode/
                #if need to identify specific qr code for ftc check here and try to identifiy
                if 500>p.astype(int)[0][0]>200 and 500>p.astype(int)[0][1]>200 and 500>p.astype(int)[1][0]>200 and 500>p.astype(int)[1][1]>200 and 500>p.astype(int)[2][0]>200 and 500>p.astype(int)[2][1]>200 and 500>p.astype(int)[3][0]>200 and 500>p.astype(int)[3][1]>200:
                    frame = cv2.putText(frame, "inside", (200,100), cv2.FONT_HERSHEY_SIMPLEX,  
                            1, (0,0,255), 2, cv2.LINE_AA) 
                elif 400>p.astype(int)[0][0]>300 and 400>p.astype(int)[0][1]>300 and 400>p.astype(int)[1][0]>300 and 400>p.astype(int)[1][1]>300 and 400>p.astype(int)[2][0]>300 and 400>p.astype(int)[2][1]>300 and 400>p.astype(int)[3][0]>300 and 400>p.astype(int)[3][1]>300:
                    frame = cv2.putText(frame, "too far away", (200,100), cv2.FONT_HERSHEY_SIMPLEX,  
                            1, (0,0,255), 2, cv2.LINE_AA) 
                else:
                    frame = cv2.putText(frame, "outside", (200,100), cv2.FONT_HERSHEY_SIMPLEX,  
                            1, (0,0,255), 2, cv2.LINE_AA) 
                

                frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
        frame = cv2.rectangle(frame,(200,200),(500,500),(0,0,255),8)
        cv2.imshow(window_name, frame)

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

cv2.destroyWindow(window_name)