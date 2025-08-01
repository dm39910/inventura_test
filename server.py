from flask_cors import CORS
from flask import Flask, request, jsonify
import csv
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route("/api/unesi", methods=["POST"])
def unesi():
    data = request.json
    timestamp = datetime.now().isoformat()
    with open("inventura.csv", "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, data["barcode"], data.get("note", "")])
    return jsonify({"status": "zabilježeno"}), 200

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
