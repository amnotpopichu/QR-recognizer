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
    <form>
    <fieldset>
        <label for="target">type to intialize:</label>
        <input id="target" type="text">
    </fieldset>
    </form>
<script type="text/javascript" src="/resources/events.js"></script>
    <script src="jquery-3.7.1.js"></script>
    <script>
        function submitData() {
            const userInput = document.getElementById('user_input').value;
            fetch('http://127.0.0.1:5000/process_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                body: JSON.stringify({ user_input: userInput }),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                // Handle the response as needed
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    
        // Prevent form submission and call submitData() instead
        document.getElementById('dataForm').addEventListener('submit', function(event) {
            event.preventDefault();
            submitData();
        });

        
        



    </script>
    
</body>
</html>"""
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