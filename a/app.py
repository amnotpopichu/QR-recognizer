from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

xTriggered = 0  # Declare xTriggered globally
console_input = ""  # Variable to store console input

@app.route('/')
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Racing Wheel Input</title>
</head>
<body>
    <h1>Racing Wheel Input</h1>
    <form id="dataForm">
        <fieldset>
            <label for="target">Turn the racing wheel:</label>
            <input id="target" type="text" style="color: transparent; text-shadow: 0 0 0 #0000;">
        </fieldset>
    </form>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script>
        var xTriggered = 0;

        // Function to handle racing wheel input
        function handleRacingWheelInput(event) {
            xTriggered++;
            var rotationValue = event.gamepad.axes[0]; // Use the first axis for rotation

            // Send racing wheel input data to the server
            $.ajax({
                type: 'POST',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({'xTriggered': xTriggered, 'rotationValue': rotationValue}),
                dataType: 'json',
                url: '/process_data',
                success: function (data) {
                    console.log('Server Response:', data);
                    document.getElementById('consoleOutput').innerText = data.message;  // Display the message in the browser
                }
            });
        }

        // Attach event listener to capture racing wheel input
        window.addEventListener("gamepadconnected", function (e) {
            console.log("Racing wheel connected!");

            // Add event listener for gamepad input
            window.addEventListener("gamepadinput", handleRacingWheelInput);
        });
        
    </script>
    <div>
        <label>Console Output:</label>
        <div id="consoleOutput"></div>
    </div>
</body>
</html>
"""

@app.route('/process_data', methods=['POST'])
def process_data():
    global xTriggered, console_input  # Access the global variables
    data = request.get_json()

    if not data or 'xTriggered' not in data or 'pressedKey' not in data:
        return jsonify({'error': 'Invalid data format'})
    
    xTriggered = data.get('xTriggered', 0)
    pressedKey = data.get('pressedKey', '')

    if pressedKey.lower() == "a":
        console_input = "left"
    elif pressedKey.lower() == "s":
        console_input = "backward"
    elif pressedKey.lower() == "w":
        console_input = "forward"
    elif pressedKey.lower() == "d":
        console_input = "right"
    elif pressedKey.lower() == "q":
        console_input = "autonomous"
    elif pressedKey.lower() == "e":
        console_input = "killing process"
        # full motor stop
    
    print(f'xTriggered: {xTriggered}, Pressed Key: {pressedKey}, Console Input: {console_input}')

    response_data = {'message': f'Data processed successfully! xTriggered: {xTriggered}, Pressed Key: {pressedKey}, Console Input: {console_input}'}
    print(response_data)  # Add this line for debugging
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
