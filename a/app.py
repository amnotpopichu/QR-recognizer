from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

xTriggered = 0  # Declare xTriggered globally

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

        // Add code to handle controller input
        window.addEventListener("gamepadconnected", function(e) {
            var gamepad = e.gamepad;
            console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
                        gamepad.index, gamepad.id,
                        gamepad.buttons.length, gamepad.axes.length);

            // Handle button presses
            window.setInterval(function() {
                var buttons = navigator.getGamepads()[0].buttons;
                buttons.forEach(function(button, index) {
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
            }, 100);
        });
    </script>
</body>
</html>
"""

@app.route('/process_data', methods=['POST'])
def process_data():
    global xTriggered  # Access the global variable
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

def motor_stop():
    pass
def autonomous(state):
    #code here:
    if state == True:
        return False
        #end atonomous
    else:
        return True
        #start autonomous
    pass

autonomous = False

def handle_keyboard_input(pressedKey):
    global autonomous
    # Handle keyboard input based on the pressed key
    if pressedKey.lower() == "a":
        print("left")
    elif pressedKey.lower() == "s":
        print("backward")
    elif pressedKey.lower() == "w":
        print("forward")
    elif pressedKey.lower() == "d":
        print("right")
    elif pressedKey.lower() == "q":
        print("autonomous")
        autonomous=autonomous(autonomous)

    elif pressedKey.lower() == "e":
        print("stopping motors")
        motor_stop()
        # full motor stop

def handle_controller_input(button_index):
    global autonomous
    # Handle controller input based on the button index
    print(f'Button pressed: {button_index}')
    if button_index == "7":
        print("forward")
    elif button_index == "6":
        print("backwards")
    elif button_index == "10":
        print("stopping motors")   
        motor_stop()
    elif button_index == "11":
        print("autonomous")   
        autonomous=autonomous(autonomous)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
