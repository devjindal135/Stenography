from flask import Flask, request, jsonify, send_from_directory
import os
import cv2
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = "/tmp"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Encryption function
def encrypt_image(img_path, message):
    img = cv2.imread(img_path)
    height, width, _ = img.shape
    max_length = height * width * 3  # Maximum characters we can store

    if len(message) > max_length:
        return None  # Message is too long

    message += "##END##"  # To mark end of the message
    m, n, z = 0, 0, 0

    for char in message:
        img[n, m, z] = ord(char)
        n = (n + 1) % height
        m = (m + 1) % width
        z = (z + 1) % 3
    
    encrypted_path = os.path.join("/tmp", 'encrypted.png')
    cv2.imwrite(encrypted_path, img)
    return encrypted_path

# Decryption function
def decrypt_image(img_path):
    img = cv2.imread(img_path)
    height, width, _ = img.shape
    message = ""
    m, n, z = 0, 0, 0

    while True:
        char = chr(img[n, m, z])
        if message.endswith("##END##"):
            break
        message += char
        n = (n + 1) % height
        m = (m + 1) % width
        z = (z + 1) % 3

    return message.replace("##END##", "")

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route("/encrypt", methods=["POST"])
def encrypt():
    file = request.files["image"]
    password = request.form["password"]
    message = request.form["message"]

    img_path = os.path.join("/tmp", file.filename)  # Save directly in /tmp
    file.save(img_path)

    encrypted_img_path = encrypt_image(img_path, message)

    if encrypted_img_path:
        with open(encrypted_img_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
        return jsonify({"success": True, "image": encoded_image})
    return jsonify({"success": False, "error": "Message too long!"})

@app.route("/decrypt", methods=["POST"])
def decrypt():
    file = request.files['image']
    password = request.form['password']
    
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(img_path)

    message = decrypt_image(img_path)
    return jsonify({"success": True, "message": message})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")


if __name__ == "__main__":
    app.run(debug=True)
