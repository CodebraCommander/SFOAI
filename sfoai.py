from flask import Flask, request, jsonify
import openai
import base64
import os
import traceback  # For better error handling
import pandas as pd  # ✅ Import pandas

# ✅ Initialize OpenAI client at the top (before defining routes)
client = openai.OpenAI()

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
            model="gpt-4o",
            messages=messages
        )

        return jsonify({"response": response.choices[0].message.content})

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in /chat: {error_details}")  # Log error details
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    analysis_instructions = request.form.get("file-analysis-instructions", "Analyze the uploaded document and summarize key points.")  # ✅ Updated default instruction

    # ✅ Check file extension before processing
    filename = file.filename
    file_extension = filename.split(".")[-1].lower()

    if file_extension in ["xlsx", "xls"]:
        try:
            # ✅ Read Excel file using pandas
            df = pd.read_excel(file)
            extracted_data = df.to_dict(orient="records")  # Convert to JSON format

            # ✅ Send extracted JSON to OpenAI
            response = client.chat.completions.create(
                model="gpt-4o",  # ✅ Always using GPT-4o
                messages=[
                    {"role": "system", "content": f"{analysis_instructions}"},  # ✅ Custom user instructions
                    {"role": "user", "content": f"Here is the extracted data in JSON format: {str(extracted_data)}"}
                ]
            )
            return jsonify({"summary": response.choices[0].message.content, "extracted_data": extracted_data})
        
        except Exception as e:
            return jsonify({"error": f"Failed to process Excel file: {str(e)}"}), 500

    else:
        # ✅ Handle non-Excel files normally
        file_content = base64.b64encode(file.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",  # ✅ Always using GPT-4o
            messages=[
                {"role": "system", "content": f"{analysis_instructions}"},  # ✅ Custom user instructions
                {"role": "user", "content": f"File content (base64-encoded): {file_content}"}
            ]
        )

        return jsonify({"summary": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(port=5000)
