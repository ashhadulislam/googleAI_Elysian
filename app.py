from flask import Flask, jsonify, request
import os
import requests

import google.generativeai as genai

GOOGLE_API_KEY='***'
genai.configure(api_key=GOOGLE_API_KEY)


app = Flask(__name__)

context='''
Imagine you are a chatbot and buddy for elderly can you communicate with me with empathy, don't give me suggestions, just listen and show understanding. Now respond to the following prompt\n'''


@app.route('/generate-content', methods=['POST'])
def generate_content():
    # Extract the text from the POST request's JSON body
    request_data = request.get_json()
    input_text = request_data.get('text', 'Tell me a joke')  # Default text if none provided

    # Set the headers using environment variables
    headers = {
        'Authorization': 'Bearer ' + os.environ['access_token'],
        'Content-Type': 'application/json',
        'x-goog-user-project': os.environ['project_id']
    }
    
    # Base URL from environment variable
    base_url = os.environ['base_url']
    
    # Name of the model
    name = "tunedModels/generate-num-5356"
    
    # Construct the full URL
    full_url = f'{base_url}/v1beta/{name}:generateContent'
    meta_prompt=context+input_text
    # Data to be sent in the request
    data = {
        "contents": [{
            "parts": [{
                "text": meta_prompt
            }]
        }]
    }
    
    # Make the POST request
    response = requests.post(url=full_url, headers=headers, json=data)
    
    # Check for a successful response
    if response.ok:
        # Parse the JSON response
        response_json = response.json()
        
        # Extract the text of the first candidate (if available)
        joke_text = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No answer found.")
    else:
        # If response is not successful, return the error
        joke_text = f"Failed to generate content: {response.status_code}"

    # Return the joke as a response
    return jsonify({"Answer": joke_text})

@app.route('/test', methods=['POST',"GET"])
def test():
    return "Test success"

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    # Check if the request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # If the user does not select a file, the browser submits an empty
    # part without a filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Optionally, process or save the file
        filename = file.filename
        filepath = os.path.join('rec_audios/', filename)
        file.save(filepath)
        sample_file = genai.upload_file(path=filepath,
                            display_name="Sample drawing")

        print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")

        prompt = "Listen carefully to the following audio file. Transcribe and convert speech to text. Give the trascript, no extra text"
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
        response = model.generate_content([prompt, sample_file])
        print(response.text)
        if "Okay, here is the transcript:" in response.text:
            ans=response.text.replace("Okay, here is the transcript:","")
        else:
            ans=response.text


        
        input_text=ans
        meta_prompt=context+input_text
        print(f"Sending to server:\n {meta_prompt}")
        response = model.generate_content([meta_prompt])
        print(response.text)
        return jsonify({"Answer": response.text})
        


if __name__ == '__main__':
    # Run the Flask server on port 5000
    app.run(host='0.0.0.0',port=5000, debug=True)
