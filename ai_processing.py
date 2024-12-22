from flask import Flask, request, jsonify
import openai
import os

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API Key
openai.api_key = "your_openai_api_key"  # Replace with your OpenAI API key

# Function to process email text using OpenAI
def process_text_with_openai(email_text):
    """Extract username and user ID from email text using OpenAI."""
    try:
        prompt = f"""
        Extract the following details from the email body:
        - Username
        - User ID

        Email Body:
        {email_text}
        """
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        extracted_data = response['choices'][0]['text'].strip()
        print("OpenAI Response (Text):", extracted_data)

        # Parse the extracted data using basic parsing
        username = None
        user_id = None
        for line in extracted_data.splitlines():
            if "Username" in line:
                username = line.split(":")[-1].strip()
            if "User ID" in line:
                user_id = line.split(":")[-1].strip()

        return {
            "username": username,
            "user_id": user_id,
        }
    except Exception as e:
        print(f"Error processing text with OpenAI: {e}")
        return {"username": None, "user_id": None}

# Function to process image using OpenAI
def process_image_with_openai(image_path):
    """Extract transaction details (ID, Amount) from an image using OpenAI."""
    try:
        # Open image file
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        # Send image to OpenAI API (GPT-4 Vision or similar API)
        response = openai.Image.create_completion(
            file=image_data,
            prompt="Extract the transaction ID and amount from this receipt image.",
            model="image-alpha-001"  # Adjust model based on OpenAI capabilities
        )

        # Extract data from the response
        response_text = response["choices"][0]["text"]
        print("OpenAI Response (Image):", response_text)

        # Parse transaction ID and amount
        transaction_id = None
        transaction_amount = None
        for line in response_text.splitlines():
            if "Transaction ID" in line:
                transaction_id = line.split(":")[-1].strip()
            if "Amount" in line:
                transaction_amount = line.split(":")[-1].strip()

        return {
            "transaction_id": transaction_id,
            "transaction_amount": transaction_amount,
        }
    except Exception as e:
        print(f"Error processing image with OpenAI: {e}")
        return {"transaction_id": None, "transaction_amount": None}

# API endpoint to process email text and image
@app.route("/process", methods=["POST"])
def process():
    """Process email text and image, and return JSON response."""
    try:
        # Get email text from form data
        email_text = request.form.get("email_text")
        if not email_text:
            return jsonify({"error": "Email text is missing"}), 400

        # Save and process the image
        images = request.files.getlist("images")
        if not images:
            return jsonify({"error": "Image attachments are missing"}), 400

        # Assume one image is uploaded
        image = images[0]
        image_path = os.path.join("./temp", image.filename)
        os.makedirs("./temp", exist_ok=True)
        image.save(image_path)

        # Extract text information using OpenAI
        text_data = process_text_with_openai(email_text)

        # Extract transaction details from the image using OpenAI
        image_data = process_image_with_openai(image_path)

        # Combine the data into a JSON response
        response = {
            "username": text_data["username"],
            "user_id": text_data["user_id"],
            "transaction_id": image_data["transaction_id"],
            "transaction_amount": image_data["transaction_amount"],
        }

        # Cleanup temporary files
        os.remove(image_path)

        return jsonify(response), 200

    except Exception as e:
        print(f"Error in processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Run Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
