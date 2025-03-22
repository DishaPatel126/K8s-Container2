from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Persistent volume directory in GKE
PERSISTENT_STORAGE_PATH = "/disha_PV_dir/"

@app.route('/process', methods=['POST'])
def process():
    if request.content_type != "application/json":
        return jsonify({"file": None, "error": "Unsupported Media Type"}), 415

    try:
        data = request.get_json()
        if not data or "file" not in data or "product" not in data:
            return jsonify({"file": None, "error": "Invalid JSON input."}), 400

        file_name = data["file"]
        product = data["product"]
        file_path = os.path.join(PERSISTENT_STORAGE_PATH, file_name)

        if not os.path.isfile(file_path):
            return jsonify({"file": file_name, "error": "File not found."}), 404

        try:
            from io import StringIO
            with open(file_path, 'r') as f:
                content = f.read()
            df = pd.read_csv(StringIO(content), delimiter=",", dtype=str)

            df.columns = [col.strip().lower() for col in df.columns]

            if df.columns.tolist() != ["product", "amount"]:
                raise ValueError("Invalid CSV format")

            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
            if df["amount"].isna().any():
                raise ValueError("Invalid CSV format")

            total = df[df["product"] == product]["amount"].sum()
            return jsonify({"file": file_name, "sum": int(total)}), 200

        except Exception:
            return jsonify({"file": file_name, "error": "Input file not in CSV format."}), 400

    except Exception as e:
        return jsonify({"file": None, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
