from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os, csv, time, threading

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# === PUTANJE (prilagodi po potrebi) ==========================================
# Lokacija za PISANJE (lokalni, nesinkronizirani folder na Z400)
LOCAL_DIR = r"C:\InventuraLocal"
LOCAL_CSV = os.path.join(LOCAL_DIR, "inventura_local.csv")

# OneDrive sink folder (SINKRONIZIRANA kopija koju čitaju Excel/Access)
ONEDRIVE_DIR = r"C:\Users\JA\OneDrive - Hrvatska kontrola zračne plovidbe d.o.o\Inventura"
ONEDRIVE_CSV = os.path.join(ONEDRIVE_DIR, "inventura.csv")

# Interval sinkronizacije (sekunde)
SYNC_INTERVAL = 60
# ============================================================================

def ensure_csv_with_header(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write("timestamp,barcode,note\n")

# Kreiraj oba CSV-a (ako ne postoje)
ensure_csv_with_header(LOCAL_CSV)
os.makedirs(ONEDRIVE_DIR, exist_ok=True)
ensure_csv_with_header(ONEDRIVE_CSV)

def append_local_row(row):
    """Jednostavno i brzo dodavanje u LOKALNI CSV (bez OneDrive lockova)."""
    with open(LOCAL_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def sync_worker():
    """Periodički kopira LOCAL_CSV u ONEDRIVE_CSV atomski (tmp→replace)."""
    print(f"[SYNC] Start; interval={SYNC_INTERVAL}s")
    last_mtime_sent = 0.0
    while True:
        try:
            if os.path.exists(LOCAL_CSV):
                local_mtime = os.path.getmtime(LOCAL_CSV)
                # šalji samo ako je lokalni noviji od zadnje poslane verzije
                if local_mtime > last_mtime_sent:
                    tmp_path = ONEDRIVE_CSV + ".synctmp"
                    # čitaj sve iz lokalnog i upiši u tmp u OneDrive mapi
                    with open(LOCAL_CSV, "rb") as src, open(tmp_path, "wb") as dst:
                        dst.write(src.read())
                    # atomska zamjena – minimizira lock/konflikte
                    os.replace(tmp_path, ONEDRIVE_CSV)
                    os.utime(ONEDRIVE_CSV, None)
                    last_mtime_sent = local_mtime
                    print(f"[SYNC] Pushed to OneDrive at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print("[SYNC][ERROR]", e)
        time.sleep(SYNC_INTERVAL)

@app.route("/")
def root():
    # (opcionalno posluži index.html iz istog foldera ako ga imaš)
    if os.path.exists(os.path.join(".", "index.html")):
        return send_from_directory(".", "index.html")
    return jsonify({"status": "OK", "msg": "Inventura API"})

@app.route("/api/unesi", methods=["POST"])
def unesi():
    data = request.get_json(silent=True) or {}
    barcode = data.get("barcode", "").strip()
    note = data.get("note", "")

    timestamp = datetime.now().isoformat()
    print(f"[PRIMLJENO] {timestamp} | Barkod: {barcode} | Napomena: {note}")

    if not barcode:
        return jsonify({"status": "bad_request", "msg": "missing barcode"}), 400

    try:
        append_local_row([timestamp, barcode, note])
        return jsonify({"status": "zabilježeno"}), 200
    except Exception as e:
        print("[CSV][ERROR]", e)
        return jsonify({"status": "error", "msg": "csv_write_failed"}), 500

@app.route("/test", methods=["GET"])
def test():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    # pokreni sync thread
    t = threading.Thread(target=sync_worker, daemon=True)
    t.start()

    # Pokreni HTTPS na 8443 s tvojim certifikatom (kao i do sada)
    # Ako želiš testno HTTP, zamijeni s: app.run(host="0.0.0.0", port=5000)
    print("API server na https://0.0.0.0:8443")
    app.run(host="0.0.0.0", port=8443, ssl_context=("cert.pem", "key.pem"))
