from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # Process login logic here
    return jsonify({"message": "Login successful"}), 200    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
