from flask import Flask, request, jsonify, render_template, Response
import logging
from flask_cors import CORS
import cv2
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])
#set strafing mode to false
#speed = maxspeed
strafe = False
input = "Manual"
#for removing ip logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
xTriggered = 0  
autonomous = False
camera_id = 0
delay = 1
qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture(camera_id)
success, frame = cap.read()
height, width, channels = frame.shape
#make this thing do stuff using height and width
sizex = int(width)//4
sizey= sizex
startx = (int(width)//2)-(sizex//2)
starty = (int(height)//2)-(sizex//2)+int(height)//5
corner1x=startx
corner1y=starty
corner2x=startx+sizex
corner2y=starty+sizex
margin=(corner2x-corner1x)/10
targetcenterx=(corner1x+corner2x)/2
targetcentery=(corner1y+corner2y)/2
movex = 0
movey = 0
detection = False
def gen_frames():  # generate frame by frame from camera
    global margin, corner1x, corner1y, corner2x, corner2y, movex, movey, detection, input
    while True:
        success, frame = cap.read()  # read the camera frame
        
        
        if not success:
            break
        else:
            ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
            #frame = cv2.rectangle(frame, (corner1x+50, corner1y+50), (corner2x-50, corner2y-50), (0, 0, 255), 8)
            fraction = 1/6  


            x_adjustment = fraction * (corner2x - corner1x)
            y_adjustment = fraction * (corner2y - corner1y)
            corner1xajust=int(corner1x + x_adjustment)
            corner1yajust=int(corner1y + y_adjustment)
            corner2xajust=int(corner2x - x_adjustment)
            corner2yajust=int(corner2y - y_adjustment)
            #minibox
            frame = cv2.rectangle(frame, 
                                (corner1xajust, corner1yajust), 
                                (corner2xajust, corner2yajust), 
                                (0, 0, 255), 8)


            #big box
            frame = cv2.rectangle(frame, (corner1x, corner1y), (corner2x, corner2y), (0, 0, 255), 8)

            if ret_qr:
                for s, p in zip(decoded_info, points):
                    color = (0, 255, 0)
                    values = p.astype(int)
                    centerx = ((int(values[0][0]) + int(values[1][0]))) / 2
                    centery = ((int(values[0][1]) + int(values[3][1]))) / 2
                    movex = targetcenterx - centerx
                    movey = targetcentery-centery
                    if targetcenterx - centerx < -margin:
                        text = "move left"
                    elif targetcenterx - centerx > margin:
                        text = "move right"
                    else:
                        text = "center x value aligned"
                    #x value move
                    frame = cv2.putText(frame, text, (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    if targetcentery-centery < -margin:
                        text = "move up"
                    elif targetcentery-centery > margin:
                        text = "move down"
                        #move forward
                    else:
                        text = "center y value aligned"
                    #y value move
                    frame = cv2.putText(frame, text, (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    
                    frame = cv2.putText(frame, input, (400, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    #center of qr box
                    frame = cv2.rectangle(frame, (int(centerx),int(centery)), (int(centerx)+10,int(centery)+10), color=(255, 0, 0), thickness=10)
                    
                    #if not so that it deonst show garbage for alinged
                    if not -margin<=targetcenterx - centerx<=margin:
                        frame = cv2.putText(frame, str(abs(targetcenterx - centerx)), (600, 100), cv2.FONT_HERSHEY_SIMPLEX,
                                            1, (0, 0, 255), 2, cv2.LINE_AA)
                    if not -margin<=targetcentery-centery<=margin:
                        frame = cv2.putText(frame, str(abs(targetcentery - centery)), (600, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                            1, (0, 0, 255), 2, cv2.LINE_AA)
                    #is qr outside
                    if any(values[i][0] < corner1x or values[i][0] > corner2x or values[i][1] < corner1y or
                           values[i][1] > corner2y for i in range(4)):
                        text = "outside"
                    #is qr aligned and inside
                    elif not any(
                            corner2xajust > values[i][0] > corner1xajust and corner2yajust > values[i][1] > corner1yajust
                            for i in range(4)):
                        text = "aligned"
                    #is qr inside but not aligned
                    else:
                        text = "inside"

                    #text if its aligned
                    frame = cv2.putText(frame, text, (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    #shows qr code polygon
                    frame = cv2.polylines(frame, [p.astype(int)], True, color, 8)
                detection=True
            else:
                frame = cv2.putText(frame, "qr code not detected", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                    2, cv2.LINE_AA)
                detection=False

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/')
def index():
    template_content = render_template('index.html')

    input_content =  """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Input</title>
</head>
<body>
    <h1>wasd to move, e = full reset, q autonomous, r for enable/disable strafe, for wheel, top left button = reset, top right button = autonomous, and button "A" = strafe</h1>
    <form id="dataForm">
        <fieldset>
            <label for="target">Type to Initialize:</label>
            <input id="target" type="text" style="color: transparent; text-shadow: 0 0 0 #0000;">
        </fieldset>
    </form>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script>
    var xTriggered = 0;
    var prevTurnDirection = null;

    $("#target").on("keydown", function (event) {
        if (event.which == 13) {
            event.preventDefault();
        }
        xTriggered++;
        var pressedKey = String.fromCharCode(event.which);
        console.log("Handler for `keydown` called " + xTriggered + " time(s). Pressed Key: " + pressedKey);

//post presseed keys
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

//check if controllers exist
    if ('getGamepads' in navigator) {
        // Set the dead zone threshold
        //var threshold = 0.2;
        var threshold = 0;
        
        window.setInterval(function () {
            var gamepads = navigator.getGamepads();

            for (var i = 0; i < gamepads.length; i++) {
                var gamepad = gamepads[i];

                if (gamepad) {
                    console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
                                gamepad.index, gamepad.id,
                                gamepad.buttons.length, gamepad.axes.length);

                    // button presses
                    gamepad.buttons.forEach(function (button, index) {
                        if (button.pressed) {
                            // Send button index to the server
                            $.ajax({
                                type: 'POST',
                                contentType: 'application/json;charset=UTF-8',
                                data: JSON.stringify({'buttonIndex': index}),
                                dataType: 'json',
                                url: '/process_controller_button',
                                success: function (data) {
                                    console.log('Server Response:', data);
                                }
                            });
                        }
                    });

                    // axes to move
                    var xAxis = gamepad.axes[0];
                    var yAxis = gamepad.axes[1];

                    //deadzone
                    xAxis = Math.abs(xAxis) < threshold ? 0 : xAxis;
                    yAxis = Math.abs(yAxis) < threshold ? 0 : yAxis;

                    xAxis = Math.round(xAxis * 100) / 100;
                    yAxis = Math.round(yAxis * 100) / 100;
                    console.log(xAxis)
                    console.log('Analog Stick Values - X:', xAxis, 'Y:', yAxis);
                    $.ajax({
                        type: 'POST',
                        contentType: 'application/json;charset=UTF-8',
                        data: JSON.stringify({'xAxis': xAxis}),
                        dataType: 'json',
                        url: '/process_turning'
                        
                        });
                    

                }
            }
        }, 100);
    } else {
        console.log('Gamepad not supported');
    }
</script>




</body>
</html>
""" 
    return input_content + template_content 
@app.route('/process_data', methods=['POST'])
def process_data():

    global xTriggered, autonomous
    data = request.get_json()

    if not data or 'xTriggered' not in data or 'pressedKey' not in data:
        return jsonify({'error': 'Invalid data format'})
    
    xTriggered = data.get('xTriggered', 0)
    pressedKey = data.get('pressedKey', '')


    #keyboard input
    handle_keyboard_input(pressedKey)
    #currently removed
    #print(f'xTriggered: {xTriggered}, Pressed Key: {pressedKey}')
    #print("\n")
    response_data = {'message': f'Data processed successfully! xTriggered: {xTriggered}, Pressed Key: {pressedKey}'}
    #removed for lack of use
    #print(response_data)
    #print("\n")  
    return jsonify(response_data)

@app.route('/process_controller_button', methods=['POST'])
def process_controller_button():
    data = request.get_json()

    if not data or 'buttonIndex' not in data:
        return jsonify({'error': 'Invalid data format'})
    #button input (controller)
    button_index = data.get('buttonIndex', 0)

    handle_controller_input(button_index)

    response_data = {'message': f'Controller button processed successfully! Button Index: {button_index}'}
    #print(response_data)
    #print("\n")
    return jsonify(response_data)

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_turning', methods=['POST'])
def process_turning():
    global xAxis
    data = request.get_json()

    #if not data or 'turnDirection' not in data or 'degree' not in data:
    #    return jsonify({'error': 'Invalid data format'})

    turn_direction = data.get('xAxis', '')
    degree = abs(turn_direction)*360
    #currently keeping for debug
    '''
    print(degree)
    print("\n")
    print(turn_direction)
    print("\n")
    '''
    if turn_direction < 0:
        turn_direction = "left"
    elif turn_direction >0:
        turn_direction = "right"
    #turn_direction = left/right degree = deg of turn
    handle_turning(turn_direction, degree)

    return jsonify({'message': 'Success'})

def reset():
    global input
    global strafe
    global autonomous
    autonomous = False
    strafe = False
    input = "Manual"
    print("motors stopped, autonomous and strafe are now false.")
    #FrontLeft = 0
    #FrontRight = 0
    #RearLeft = 0
    #RearRight = 0
    pass
def runautonomous():
    global movex, detection, movey,margin
    while detection == True:
        if movex<=-margin:
            right(240)
        elif movex>=margin:
            left(240)
        if -margin<=movex<=margin:
            if movey<=-margin:
                forward()
            elif movey>=margin:
                backwards()
def autonomous_toggle(state):
    global input
    global autonomous, strafe
    if autonomous == True:
        print("Stopping autonomous and setting strafe to true")
        print("\n")
        reset()
        autonomous = False
        

    else:
        print("Starting autonomous")
        strafe = True
        print("\n")
        autonomous = True
        input = "Autonomous"
        #activate auto stuff 

def forward():
    global autonomous
    #FrontLeft = speed
    #FrontRight = speed
    #RearLeft = speed
    #RearRight = speed
    pass

def left(deg):
    speed = deg/360
    #speed*=motormaxspeed
    global strafe
    global autonomous
    if strafe == True:
        #FrontLeft = -speed
        #FrontRight = speed
        #RearLeft = speed
        #RearRight = -speed
        pass
    else:
        #FrontLeft=-speed
        #FrontRight=speed
        #RearLeft=-speed
        #Rearright=speed
        pass

def right(deg):
    speed = deg/360
    #speed*=motormaxspeed

    global strafe
    global autonomous
    if strafe == True:
        #FrontLeft = speed
        #FrontRight = -speed
        #RearLeft = -speed
        #RearRight = speed
        pass
    else:
        #FrontLeft=speed
        #FrontRight=-speed
        #RearLeft=speed
        #Rearright=-speed
        pass

def backwards():
    global autonomous
    #FrontLeft = -speed
    #FrontRight = -speed
    #RearLeft = -speed
    #RearRight = -speed
    pass

def strafe():
    global strafe
    if strafe == True:
        strafe = False
    else:
        strafe == True
    pass
def handle_keyboard_input(pressedKey):
    global autonomous
    #ingore inputs if its autonomous
    if autonomous!=True:
        if pressedKey.lower() == "a":
            print("moving left")
            print("\n")
            left(60)
        elif pressedKey.lower() == "s":
            print("moving backward")
            print("\n")
            backwards()
        elif pressedKey.lower() == "w":
            print("moving forward")
            print("\n")
            forward()
        elif pressedKey.lower() == "d":
            print("moving right")
            print("\n")
            right(60)
    if pressedKey.lower() == "q":
        print("toggling autonomous")
        print("\n")
        autonomous_toggle(autonomous)

    if pressedKey.lower() == "e":
        print("resetting")
        print("\n")
        reset()
        # full motor stop
    if pressedKey.lower() == "r":
        print("toggling strafing")
        print("\n")
        strafe()
def handle_controller_input(button_index):
    global autonomous
    #buttons wow
    print(f'Button pressed: {button_index}')
    print("\n")
    if autonomous!=True:
        if button_index == 7:
            print("moving forward")
            print("\n")
            forward()
        elif button_index == 6:
            print("moving backwards")
            print("\n")
            backwards()
    if button_index == 10:
        print("resetting")   
        print("\n")
        reset()
    if button_index == 11:
        print("toggling autonomous")   
        print("\n")
        autonomous_toggle(autonomous)
    if button_index == 0:
        print("toggling strafe")
        print("\n")
        strafe()

def handle_turning(turn_direction, degree):
    global autonomous
    #turn direction = left/right
    #deg = how many deg in that direciton
    if autonomous!=True:
        if turn_direction == 'right':
            degree = round(degree, 5)  
            print(f'Turning right at {degree} degrees')
            print("\n")
            right(degree)
        elif turn_direction == 'left':
            degree = round(degree, 5)  # round 5 places
            print(f'Turning left at {degree} degrees')
            print("\n")
            left(degree)

if __name__ == '__main__':
    #use at home
    #app.run(host='0.0.0.0', debug=True)

    #use at nueva
    app.run(debug = True)