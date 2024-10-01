from flask import Flask, request, render_template
from flask_cors import CORS
import json
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

app = Flask(__name__)
CORS(app)

# Load the model and tokenizer
model_name = "facebook/blenderbot-400M-distill"
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Initialize conversation history
conversation_history = []


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/chatbot', methods=['POST'])
def handle_prompt():
    data = request.get_data(as_text=True)
    data = json.loads(data)
    input_text = data['prompt']

    # Ensure input_text is valid
    if not input_text.strip():
        return json.dumps({"error": "Empty input text."}), 400

    # Add the user's input to the conversation history
    conversation_history.append(input_text)

    # Combine conversation history for better context
    history = " ".join(conversation_history)

    # Tokenize the input text along with conversation history
    try:
        inputs = tokenizer.encode_plus(
            history,                # Use the conversation history for context
            return_tensors="pt",     # Return PyTorch tensors
            padding="max_length",    # Pad to the model's max length
            truncation=True,         # Truncate if the input is too long
            max_length=128           # Set a smaller length for testing
        )

        print(f"Tokenized Inputs: {inputs}")  # Debugging the tokenized inputs

        # Generate the response from the model
        outputs = model.generate(**inputs)

        # Decode the response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

        # Add the model's response to the conversation history
        conversation_history.append(response)

        return json.dumps({"response": response}), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return json.dumps({"error": "Failed to generate a response."}), 500


if __name__ == '__main__':
    app.run()
