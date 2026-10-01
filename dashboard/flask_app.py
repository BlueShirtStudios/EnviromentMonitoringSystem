from flask import Flask, render_template, request

app = Flask(__name__)

# Store the latest stats in memory
latest_stats = {"temperature": "--", "status": "Waiting for Pico..."}


# Route for the Pico to send data to (e.g. http://<YOUR_COMPUTER_IP>:5000/update?temp=24.5&status=OK)
@app.route("/update")
def update():
    latest_stats["temperature"] = request.args.get("temp", "--")
    latest_stats["status"] = request.args.get("status", "OK")
    return "Received", 200


# Route to view in your browser
@app.route("/")
def home():
    return render_template("index.html", stats=latest_stats)


if __name__ == "__main__":
    # host='0.0.0.0' allows the Pico on your Wi-Fi network to connect
    app.run(host="0.0.0.0", port=5000, debug=True)