from flask import Flask, request, jsonify, render_template, Response

from flask_cors import CORS
import cv2
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

xTriggered = 0  
autonomous = False
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
def gen_frames():  # generate frame by frame from camera
    while True:

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
                    centerx = ((int(values[0][0]) + int(values[1][0]))) / 2
                    centery = ((int(values[0][1]) + int(values[3][1]))) / 2
                    if targetcenterx - centerx < 0:
                        text = "move left"
                    elif targetcenterx - centerx > 0:
                        text = "move right"
                    else:
                        text = "x value aligned"

                    frame = cv2.putText(frame, text, (400, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    if targetcentery-centery < 0:
                        text = "move up"
                    elif targetcentery-centery > 0:
                        text = "move down"
                    else:
                        text = "y value aligned"

                    frame = cv2.putText(frame, text, (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    frame = cv2.rectangle(frame, (int(centerx),int(centery)), (int(centerx)+10,int(centery)+10), color=(255, 0, 0), thickness=10)


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
    <h1>wasd to move, e = full reset, q autonomous, for wheel, top left button = reset, top right button = autonomous</h1>
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
        var threshold = 0.2;

        
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
    #can remove but is currentlly for debug
    print(f'xTriggered: {xTriggered}, Pressed Key: {pressedKey}')
    print("\n")
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
    print(degree)
    print("\n")
    print(turn_direction)
    print("\n")
    if turn_direction < 0:
        turn_direction = "left"
    elif turn_direction >0:
        turn_direction = "right"
    #turn_direction = left/right degree = deg of turn
    handle_turning(turn_direction, degree)

    return jsonify({'message': 'Success'})

def reset():
    global autonomous
    autonomous = False
    #motor stop
    pass

def autonomous_toggle(state):
    global autonomous
    if state:
        print("Stopping autonomous")
        print("\n")
        reset()
    else:
        print("Starting autonomous")
        print("\n")
        reset()
        autonomous = True
        #activate auto stuff 

def forward():
    global autonomous
    if autonomous != True:
        #all motors forward
        pass

def left(deg):
    global autonomous
    if autonomous != True:
        #right motors full forward
        #left motors full backward (time based on angles)
        pass

def right(deg):
    global autonomous
    if autonomous != True:
        #right motors full back
        #left motors full forward (time based on angles)
        pass

def backwards():
    global autonomous
    if autonomous != True:
        #all motors backward
        pass

def handle_keyboard_input(pressedKey):
    global autonomous
    if pressedKey.lower() == "a":
        print("moving left")
        print("\n")
        left(10)
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
        right(10)
    elif pressedKey.lower() == "q":
        print("toggling autonomous")
        print("\n")
        autonomous_toggle(autonomous)

    elif pressedKey.lower() == "e":
        print("resetting")
        print("\n")
        reset()
        # full motor stop

def handle_controller_input(button_index):
    global autonomous
    #buttons wow
    print(f'Button pressed: {button_index}')
    print("\n")
    if button_index == 7:
        print("moving forward")
        print("\n")
        forward()
    elif button_index == 6:
        print("moving backwards")
        print("\n")
        backwards()
    elif button_index == 10:
        print("resetting")   
        print("\n")
        reset()
    elif button_index == 11:
        print("toggling autonomous")   
        print("\n")
        autonomous_toggle(autonomous)

def handle_turning(turn_direction, degree):
    global autonomous
    #turn direction = left/right
    #deg = how many deg in that direciton
    if turn_direction == 'right':
        degree = round(degree, 2)  
        print(f'Turning right at {degree} degrees')
        print("\n")
        right(degree)
    elif turn_direction == 'left':
        degree = round(degree, 2)  # round 2 places
        print(f'Turning left at {degree} degrees')
        print("\n")
        left(degree)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)