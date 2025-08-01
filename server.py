from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route("/api/unesi", methods=["POST"])
def unesi():
    data = request.json
    timestamp = datetime.now().isoformat()
    print(f"[PRIMLJENO] {timestamp} | Barkod: {data.get('barcode')} | Napomena: {data.get('note', '')}")
    
    with open("inventura.csv", "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, data["barcode"], data.get("note", "")])
    
    return jsonify({"status": "zabilježeno"}), 200

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    print("API server pokrenut na https://0.0.0.0:8443")
    app.run(host="0.0.0.0", port=8443, ssl_context=("cert.pem", "key.pem"))
