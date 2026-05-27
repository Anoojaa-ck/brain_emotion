from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Model name
model_name = "j-hartmann/emotion-english-distilroberta-base"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Set device (GPU if available, else CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

def detect_emotion(text):
    # Tokenize input
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    inputs = {key: val.to(device) for key, val in inputs.items()}

    # Disable gradient calculation for inference
    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probabilities = F.softmax(logits, dim=1)

    predicted_class_id = torch.argmax(probabilities, dim=1).item()
    predicted_emotion = model.config.id2label[predicted_class_id]

    return predicted_emotion, probabilities.cpu().numpy()[0]


# Example usage
if __name__ == "__main__":
    text = "I feel amazing today!"
    emotion, probs = detect_emotion(text)

    print("Predicted Emotion:", emotion)
    print("Probabilities:", probs)