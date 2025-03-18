from flask import Flask, request, jsonify
import openai
import base64
import os
import traceback  # For better error handling

app = Flask(__name__)

# Ensure OpenAI API Key is set
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "SFOAI API is running."})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        messages = data.get("messages", [])
        json_format = data.get("json_format", "{}")

        system_message = {
            "role": "system",
            "content": f"You must always respond in valid JSON format: {json_format}"
        }
        messages.insert(0, system_message)

        # Use new OpenAI v1.0+ API syntax
        client = openai.OpenAI()

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages
        )

        return jsonify({"response": response.choices[0].message.content})

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in /chat: {error_details}")  # Log error details
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Read and encode file
        file_content = base64.b64encode(file.read()).decode("utf-8")

        # OpenAI API call with updated syntax
        client = openai.OpenAI()

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Analyze the uploaded document and summarize its key points."},
                {"role": "user", "content": f"File content (base64-encoded): {file_content}"}
            ]
        )

        return jsonify({"summary": response.choices[0].message.content})

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in /upload: {error_details}")  # Log error details
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
