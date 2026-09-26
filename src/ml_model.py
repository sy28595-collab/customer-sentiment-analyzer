from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def create_vectorizer():
    return TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True
    )

def create_model():
    return LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    )

def train_model(messages, labels):
    vectorizer = create_vectorizer()
    X = vectorizer.fit_transform(messages)
    model = create_model()
    model.fit(X, labels)
    return vectorizer, model

def predict(messages, vectorizer, model):
    X = vectorizer.transform(messages)
    return model.predict(X)