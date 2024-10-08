from transformers import pipeline

# Explicitly specify the model and revision for sentiment analysis
sentiment_analyzer = pipeline(
    'sentiment-analysis',
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    revision="714eb0f"
)

# Function to analyze public feedback and return sentiment
def analyze_feedback(feedback_text):
    if feedback_text and len(feedback_text) > 5:  # Validate input length
        result = sentiment_analyzer(feedback_text)
        label = result[0]['label']
        score = result[0]['score']
        return label, score
    else:
        return "Neutral", 0.0  # Default if feedback is empty or too short


