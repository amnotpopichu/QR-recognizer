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
    <title>input</title>
</head>
<body>
    <h1>input</h1>
    <form id="dataForm">
        <fieldset>
            <label for="target">type to initialize:</label>
            <input id="target" type="text" style="color: transparent; text-shadow: 0 0 0 #0000;"> <!-- Set type to text and hide characters visually -->
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
            var pressedKey = String.fromCharCode(event.which); // Get the pressed key
            var msg = "Handler for `keydown` called " + xTriggered + " time(s). Pressed Key: " + pressedKey;
            console.log(msg);
            console.log(event);

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

    if pressedKey.lower() == "a":
        print("left")
    if pressedKey.lower() == "s":
        print("backward")
    if pressedKey.lower() == "w":
        print("forward")
    if pressedKey.lower() == "d":
        print("right")
    if pressedKey.lower() == "q":
        print("autonomous")
    if pressedKey.lower() == "e":
        print("killing process")
        # full motor stop
    
    print(f'xTriggered: {xTriggered}, Pressed Key: {pressedKey}')

    response_data = {'message': f'Data processed successfully! xTriggered: {xTriggered}, Pressed Key: {pressedKey}'}
    print(response_data)  # Add this line for debugging
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
