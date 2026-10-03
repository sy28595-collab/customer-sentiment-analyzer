import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download("vader_lexicon", quiet=True)

sia = SentimentIntensityAnalyzer()

def get_vader_score(text):
    return sia.polarity_scores(text)["compound"]

def get_sentiment(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    return "Neutral"

def analyze_sentiment(text):
    score = get_vader_score(text)
    return score, get_sentiment(score)