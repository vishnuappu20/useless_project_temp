from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify(message="Hello from Flask on Vercel!")

# Vercel expects a variable named 'app'
# No need to call app.run()
