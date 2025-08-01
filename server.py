from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import csv
from datetime import datetime
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

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
    print(f"Server pokrenut na https://192.168.1.205:8443")
    app.run(host="0.0.0.0", port=8443, ssl_context=("cert.pem", "key.pem"))
