import os
import sys
import sqlite3
from datetime import datetime

import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from src.vader_sentiment import analyze_sentiment

DATABASE_PATH = os.path.join(BASE_DIR, "database", "sentiment.db")

def save_review(review, sentiment, rating):
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT,
            sentiment TEXT,
            rating TEXT,
            created_at TEXT
        )
    """)
    columns = [row[1] for row in cursor.execute("PRAGMA table_info(reviews)")]
    if "rating" not in columns:
        cursor.execute("ALTER TABLE reviews ADD COLUMN rating TEXT")
    cursor.execute(
        """
        INSERT INTO reviews (review, sentiment, rating, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            review,
            sentiment,
            rating,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    conn.commit()
    cursor.execute("""
        DELETE FROM reviews
        WHERE id NOT IN (
            SELECT id
            FROM reviews
            ORDER BY id DESC
            LIMIT 1000
        )
    """)
    conn.commit()
    conn.close()

st.set_page_config(
    page_title="Customer Feedback",
    page_icon="💬",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: #F5F0E8;
}

.block-container {
    max-width: 760px;
    padding-top: 4rem;
    padding-bottom: 1rem;
}

.main-title {
    text-align: center;
    font-size: 34px;
    font-weight: 700;
    color: #2C2925;
    margin-top: 10px;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 15px;
    color: #746F68;
    margin-bottom: 25px;
}

.question {
    text-align: center;
    font-size: 18px;
    font-weight: 600;
    color: #2C2925;
    margin-bottom: 12px;
}

div.stButton > button {
    height: 115px;
    border-radius: 18px;
    border: 1px solid #DDD5C8;
    background: #FFFDF8;
    color: #2C2925;
    font-size: 21px;
    font-weight: 500;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: #E9DFD0;
    border-color: #8B7A65;
    transform: translateY(-2px);
}

.selected-text {
    text-align: center;
    color: #746F68;
    font-size: 13px;
    margin-top: 8px;
}

.review-title {
    font-size: 17px;
    font-weight: 600;
    color: #2C2925;
    margin-top: 20px;
    margin-bottom: 7px;
}

textarea {
    border-radius: 15px !important;
}

div.stButton > button[kind="primary"] {
    height: 46px;
    border-radius: 23px;
    background: #2C2925;
    color: white;
    border: none;
    font-size: 16px;
}

div.stButton > button[kind="primary"]:hover {
    background: #45403A;
}

.stAlert {
    background: #FFF8E7 !important;
    color: #5C4610 !important;
    border: 1px solid #E6D39A !important;
}

.stAlert p {
    color: #5C4610 !important;
}

.success-card {
    background: #FFFDF8;
    border: 1px solid #DDD5C8;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin-top: 15px;
}

.success-icon {
    font-size: 28px;
    color: #5E7655;
}

.success-title {
    font-size: 20px;
    font-weight: 600;
    color: #2C2925;
}

.success-text {
    color: #746F68;
    font-size: 14px;
    margin-top: 4px;
}

.footer {
    text-align: center;
    color: #746F68;
    font-size: 12px;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">We’d love to hear from you.</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your feedback helps us create a better experience.</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="question">How was your experience?</div>',
    unsafe_allow_html=True
)

emoji_options = {
    "😞": "Not great",
    "😐": "Okay",
    "😊": "Great"
}

if "selected_emoji" not in st.session_state:
    st.session_state.selected_emoji = "😊"

cols = st.columns(3)

for col, (emoji, label) in zip(cols, emoji_options.items()):
    with col:
        if st.button(
            f"{emoji}\n\n{label}",
            key=f"emoji_{emoji}",
            use_container_width=True
        ):
            st.session_state.selected_emoji = emoji
            st.rerun()

st.markdown(
    f'<div class="selected-text">Selected: {emoji_options[st.session_state.selected_emoji]}</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="review-title">Tell us more about your experience</div>',
    unsafe_allow_html=True
)

review = st.text_area(
    "Review",
    placeholder="Share your thoughts...",
    height=120,
    max_chars=500,
    label_visibility="collapsed"
)

if st.button(
    "Submit Feedback →",
    type="primary",
    use_container_width=True
):
    if review.strip():
        score, prediction = analyze_sentiment(review)
    else:
        prediction = "Neutral"

    save_review(
        review.strip(),
        prediction,
        st.session_state.selected_emoji
    )

    st.markdown("""
    <div class="success-card">
        <div class="success-icon">✓</div>
        <div class="success-title">Thank you.</div>
        <div class="success-text">
            Your feedback has been received.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    '<div class="footer">Every piece of feedback helps us improve.</div>',
    unsafe_allow_html=True
)