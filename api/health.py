from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/health")
def health():
    return jsonify({"status": "alive", "version": "1.0.1"}), 200

if __name__ == "__main__":
    app.run(debug=True)
