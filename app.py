# Import the required packages
import os
import openai
import requests
from flask import Flask, render_template, request

# Initialize the Flask app
app = Flask(__name__)

# Set the OpenAI API key and organization ID
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")

# Define the endpoints for the app
@app.route("/")
def index():
    # Render the index.html template
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    # Get the user input from the form
    user_input = request.form.get("user_input")

    # Generate a text/story completion using the GPT3.5 API
    text_response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=user_input,
        max_tokens=100,
        temperature=0.9,
        stop="\n"
    )

    # Get the text from the response
    text = text_response["choices"][0]["text"]

    # Generate an image using the Dall-E 3 API
    image_response = requests.post(
        "https://api.openai.com/v1/dalle-3/images",
        headers={
            "Authorization": f"Bearer {openai.api_key}",
            "OpenAI-Organization": openai.organization
        },
        json={
            "text": user_input + text
        }
    )

    # Get the image URL from the response
    image_url = image_response.json()["image_url"]

    # Render the generate.html template with the text and image
    return render_template("generate.html", text=text, image_url=image_url)
