from flask import Flask, request, jsonify
import openai
import base64

app = Flask(__name__)
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "SFOAI API is running."})

from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Ensure OpenAI API Key is set
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
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


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    file_content = base64.b64encode(file.read()).decode("utf-8")

    # Example of sending a file as context (GPT-4-turbo with vision required)
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Analyze the uploaded document and summarize its key points."},
            {"role": "user", "content": f"File content (base64-encoded): {file_content}"}
        ]
    )

    return jsonify({"summary": response["choices"][0]["message"]["content"]})

if __name__ == "__main__":
    app.run(port=5000)
