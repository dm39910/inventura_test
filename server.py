from flask import Flask, request, jsonify
import csv
from datetime import datetime

app = Flask(__name__)

@app.route('/api/unesi', methods=['POST'])
def unesi():
    data = request.get_json()
    barcode = data.get('barcode')
    note = data.get('note')
    timestamp = datetime.now().isoformat()
    
    with open('log.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, barcode, note])
    
    return jsonify({'status': 'OK'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
