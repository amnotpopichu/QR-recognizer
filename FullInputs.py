from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

xTriggered = 0  
autonomous = False

@app.route('/')
def index():
    return """<!DOCTYPE html>
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