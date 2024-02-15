from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

xTriggered = 0  # Declare xTriggered globally
autonomous = False
prev_turn_direction = None  # Variable to store the previous turning state

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
    <h1>Input</h1>
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

        // Now, send the xTriggered value and pressedKey to the server
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

    // Check gamepad support
    if ('getGamepads' in navigator) {
        // Set the dead zone threshold
        var threshold = 0.2;

        // Start the gamepad detection loop
        window.setInterval(function () {
            var gamepads = navigator.getGamepads();

            for (var i = 0; i < gamepads.length; i++) {
                var gamepad = gamepads[i];

                if (gamepad) {
                    console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
                                gamepad.index, gamepad.id,
                                gamepad.buttons.length, gamepad.axes.length);

                    // Handle button presses
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

                    // Handle analog stick input with dead zone
                    var xAxis = gamepad.axes[0];
                    var yAxis = gamepad.axes[1];

                    // Apply dead zone
                    xAxis = Math.abs(xAxis) < threshold ? 0 : xAxis;
                    yAxis = Math.abs(yAxis) < threshold ? 0 : yAxis;

                    // Round to the 100th decimal place
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

    global xTriggered, autonomous  # Access the global variables
    data = request.get_json()

    if not data or 'xTriggered' not in data or 'pressedKey' not in data:
        return jsonify({'error': 'Invalid data format'})
    
    xTriggered = data.get('xTriggered', 0)
    pressedKey = data.get('pressedKey', '')



    # Handle keyboard input
    handle_keyboard_input(pressedKey)

    print(f'xTriggered: {xTriggered}, Pressed Key: {pressedKey}')

    response_data = {'message': f'Data processed successfully! xTriggered: {xTriggered}, Pressed Key: {pressedKey}'}
    print(response_data)  # Add this line for debugging
    return jsonify(response_data)

@app.route('/process_controller_button', methods=['POST'])
def process_controller_button():
    data = request.get_json()

    if not data or 'buttonIndex' not in data:
        return jsonify({'error': 'Invalid data format'})

    button_index = data.get('buttonIndex', 0)

    # Handle controller button input
    handle_controller_input(button_index)

    response_data = {'message': f'Controller button processed successfully! Button Index: {button_index}'}
    print(response_data)
    return jsonify(response_data)

@app.route('/process_turning', methods=['POST'])
def process_turning():
    global xAxis
    data = request.get_json()

    #if not data or 'turnDirection' not in data or 'degree' not in data:
    #    return jsonify({'error': 'Invalid data format'})

    turn_direction = data.get('xAxis', '')
    degree = abs(turn_direction)*360
    print(degree)
    print(turn_direction)
    if turn_direction < 0:
        turn_direction = "left"
    elif turn_direction >0:
        turn_direction = "right"


    # Handle turning based on the received direction and degree
    handle_turning(turn_direction, degree)

    return jsonify({'message': 'Success'})

def reset():
    global autonomous
    autonomous = False
    pass

def autonomous_toggle(state):
    global autonomous
    if state:
        print("Stopping autonomous")
        autonomous = False
    else:
        print("Starting autonomous")
        autonomous = True

def forward():
    if autonomous != True:
        #movzies
        pass

def left(deg):
        if autonomous != True:

           pass

def right(deg):
        if autonomous != True:

         pass

def backwards():
        if autonomous != True:

            pass

def handle_keyboard_input(pressedKey):
    global autonomous
    # Handle keyboard input based on the pressed key
    if pressedKey.lower() == "a":
        print("left")
        left(10)
    elif pressedKey.lower() == "s":
        print("backward")
        backwards()
    elif pressedKey.lower() == "w":
        print("forward")
        forward()
    elif pressedKey.lower() == "d":
        print("right")
        right(10)
    elif pressedKey.lower() == "q":
        print("Toggle autonomous")
        autonomous_toggle(autonomous)

    elif pressedKey.lower() == "e":
        print("resetting")
        reset()
        # full motor stop

def handle_controller_input(button_index):
    global autonomous

    # Handle controller input based on the button index
    print(f'Button pressed: {button_index}')
    if button_index == 7:
        print("forward")
        forward()
    elif button_index == 6:
        print("backwards")
        backwards()
    elif button_index == 10:
        print("resetting")   
        reset()
    elif button_index == 11:
        print("autonomous")   
        autonomous_toggle(autonomous)

def handle_turning(turn_direction, degree):
    # Handle turning based on the received direction and degree
    global autonomous
    if turn_direction == 'right':
        degree = round(degree, 2)  # Round to the 100th decimal place
        print(f'Turning right at {degree} degrees')
        right(degree)
        # Add your logic for turning right
    elif turn_direction == 'left':
        degree = round(degree, 2)  # Round to the 100th decimal place
        left(degree)
        print(f'Turning left at {degree} degrees')
        # Add your logic for turning left

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)