from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

#Global memory storage for the latest Pico reading
latest_data = {
    "motion_detected": False,
    "temperature": 0.0,
    "humidity": 0.0,
    "light_percentage": 0.0
}

@app.route('/')
def dashboard():
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Environment Monitor Dashboard</title>
        <!-- Auto-refresh page every 3 seconds to pull fresh data -->
        <meta http-equiv="refresh" content="3">
        <style>
            body { font-family: Arial, sans-serif; background: #f4f7f6; margin: 40px; text-align: center; }
            h1 { color: #333; }
            .grid { display: flex; justify-content: center; gap: 20px; margin-top: 30px; flex-wrap: wrap; }
            .card { background: white; padding: 25px; border-radius: 10px; width: 180px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .value { font-size: 28px; font-weight: bold; color: #007bff; margin-top: 10px; }
            .motion-alert { color: #dc3545; }
            .motion-clear { color: #28a745; }
        </style>
    </head>
    <body>
        <h1>Pico W Environment Monitor</h1>
        <p>Live IoT Telemetry Dashboard</p>
        
        <div class="grid">
            <div class="card">
                <div>Motion</div>
                <div class="value {{ 'motion-alert' if data.motion_detected else 'motion-clear' }}">
                    {{ 'ALERT' if data.motion_detected else 'CLEAR' }}
                </div>
            </div>
            <div class="card">
                <div>Temperature</div>
                <div class="value">{{ data.temperature }} °C</div>
            </div>
            <div class="card">
                <div>Humidity</div>
                <div class="value">{{ data.humidity }} %</div>
            </div>
            <div class="card">
                <div>Light Level</div>
                <div class="value">{{ data.light_percentage }} %</div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, data=latest_data)

@app.route('/api/data', methods=['POST'])
def receive_data():
    global latest_data
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No JSON payload received"}), 400

    # Store payload into global memory
    latest_data["motion_detected"] = data.get('detected_motion', False)
    latest_data["temperature"] = data.get('temperature', 0.0)
    latest_data["humidity"] = data.get('humidity', 0.0)
    latest_data["light_percentage"] = data.get('light_percentage', 0.0)

    print("Payload logged successfully.")
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)