import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vader_sentiment import get_sentiment, analyze_sentiment

def test_positive_sentiment():
    score, sentiment = analyze_sentiment("I love this product. Excellent service!")
    assert sentiment == "Positive"

def test_negative_sentiment():
    score, sentiment = analyze_sentiment("This product is terrible and very bad.")
    assert sentiment == "Negative"

def test_neutral_sentiment():
    score, sentiment = analyze_sentiment("The product is abailable .")
    assert sentiment == "Neutral"

def test_sentiment_threshold():
    assert get_sentiment(0.05) == "Positive"
    assert get_sentiment(-0.05) == "Negative"
    assert get_sentiment(0) == "Neutral"