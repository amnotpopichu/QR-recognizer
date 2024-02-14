from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

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
            <input id="target" type="text">
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
            var msg = "Handler for `keydown` called " + xTriggered + " time(s).";
            console.log(msg);
            console.log(event);
        });
    </script>
</body>
</html>
"""
@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.get_json()

    if not data or 'user_input' not in data:
        return jsonify({'error': 'Invalid data format'})
    #user_input used for movement
    user_input = data.get('user_input', '')
    print(f'User Input: {user_input}')

    response_data = {'message': f'Data processed successfully! User input: {user_input}'}
    print(response_data)  # Add this line for debugging
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)