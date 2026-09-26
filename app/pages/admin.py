import os
import json
import sqlite3
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "sentiment.db")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORT_PATH = os.path.join(PROCESSED_DIR, "classification_report.json")
CONFUSION_PATH = os.path.join(PROCESSED_DIR, "confusion_matrix.csv")
ACCURACY_PATH = os.path.join(PROCESSED_DIR, "accuracy.txt")
COMPARISON_PATH = os.path.join(PROCESSED_DIR, "comparison_results.csv")

st.set_page_config(page_title="Sentiment Analytics", page_icon="📊", layout="wide")

st.markdown("""
<style>
.stApp {background:#F5F0E8;}
.block-container {max-width:1400px;padding-top:4rem;padding-bottom:2rem;}
.main-title {font-size:34px;font-weight:700;color:#2C2925;text-align:center;margin-bottom:6px;}
.subtitle {color:#746F68;font-size:15px;text-align:center;margin-bottom:25px;}
.subtitle {color:#746F68;font-size:15px;margin-bottom:25px;}
.section-title {font-size:22px;font-weight:650;color:#2C2925;margin-top:25px;margin-bottom:14px;}
.metric-card {background:#FFFDF8;border:1px solid #DDD5C8;border-radius:16px;padding:20px;min-height:110px;}
.metric-label {color:#746F68;font-size:14px;margin-bottom:8px;}
.metric-value {color:#2C2925;font-size:30px;font-weight:700;}

.sentiment-chart {
    background:#FFFDF8;
    border:1px solid #DDD5C8;
    border-radius:16px;
    padding:24px 35px 20px;
    height:270px;
    display:flex;
    align-items:flex-end;
    justify-content:space-around;
    gap:80px;
}
.sentiment-column {
    height:225px;
    flex:1;
    max-width:220px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:flex-end;
}
.sentiment-value {font-size:15px;font-weight:700;color:#2C2925;margin-bottom:8px;}
.sentiment-bar-area {height:165px;width:100%;display:flex;align-items:flex-end;justify-content:center;}
.sentiment-bar {width:68px;border-radius:10px 10px 4px 4px;}
.negative-bar {background:#D96B62;}
.neutral-bar {background:#B9A7D1;}
.positive-bar {background:#72B487;}
.sentiment-label {margin-top:12px;font-size:14px;font-weight:600;color:#2C2925;}

[data-testid="stTextInput"] label p,
[data-testid="stSelectbox"] label p {color:#2C2925 !important;font-weight:600 !important;}
[data-testid="stTextInput"] input {
    background:#FFFDF8 !important;
    color:#2C2925 !important;
    border:1px solid #BDB4A7 !important;
    border-radius:10px !important;
}
[data-testid="stTextInput"] input::placeholder {color:#8E877F !important;}
[data-baseweb="select"] {background:#FFFDF8 !important;border-radius:10px !important;}
[data-baseweb="select"] * {color:#2C2925 !important;}

[data-testid="stExpander"] {
    background:#FFFDF8 !important;
    border:1px solid #DDD5C8 !important;
    border-radius:14px !important;
    margin-bottom:10px;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span {color:#2C2925 !important;}
[data-testid="stExpander"] summary p {font-weight:600 !important;}

[data-testid="stDataFrame"] {border:1px solid #DDD5C8;border-radius:12px;overflow:hidden;}

.info-card {
    background:#FFFDF8;
    border:1px solid #DDD5C8;
    border-radius:16px;
    padding:22px;
    color:#2C2925 !important;
    line-height:1.5;
}
.info-card b {color:#2C2925 !important;}
.stAlert {border-radius:12px;}
hr {border-color:#DDD5C8;}
</style>
""", unsafe_allow_html=True)

def load_reviews():
    if not os.path.exists(DATABASE_PATH):
        return pd.DataFrame(columns=["id","review","sentiment","rating","created_at"])
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM reviews ORDER BY id DESC", conn)
    conn.close()
    if "rating" not in df.columns:
        df["rating"] = ""
    return df

def load_model_metrics():
    accuracy = None
    report = None
    confusion = None
    if os.path.exists(ACCURACY_PATH):
        with open(ACCURACY_PATH, "r") as f:
            accuracy = float(f.read())
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r") as f:
            report = json.load(f)
    if os.path.exists(CONFUSION_PATH):
        confusion = pd.read_csv(CONFUSION_PATH, index_col=0)
    return accuracy, report, confusion

reviews_df = load_reviews()
accuracy, report, confusion = load_model_metrics()

st.markdown('<div class="main-title">📊 Customer Sentiment Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Customer feedback and sentiment analysis dashboard</div>', unsafe_allow_html=True)
st.divider()

total_reviews = len(reviews_df)
positive_count = (reviews_df["sentiment"] == "Positive").sum()
neutral_count = (reviews_df["sentiment"] == "Neutral").sum()
negative_count = (reviews_df["sentiment"] == "Negative").sum()

st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
metrics = [
    ("Total Reviews", total_reviews),
    ("Positive", positive_count),
    ("Neutral", neutral_count),
    ("Negative", negative_count)
]

for col, (label, value) in zip([col1, col2, col3, col4], metrics):
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',
            unsafe_allow_html=True
        )

st.markdown('<div class="section-title">Sentiment Distribution</div>', unsafe_allow_html=True)

if total_reviews > 0:
    max_count = max(positive_count, neutral_count, negative_count, 1)
    negative_height = max(12, int((negative_count / max_count) * 150))
    neutral_height = max(12, int((neutral_count / max_count) * 150))
    positive_height = max(12, int((positive_count / max_count) * 150))

    st.markdown(
        f"""
        <div class="sentiment-chart">
            <div class="sentiment-column">
                <div class="sentiment-value">{negative_count}</div>
                <div class="sentiment-bar-area">
                    <div class="sentiment-bar negative-bar" style="height:{negative_height}px;"></div>
                </div>
                <div class="sentiment-label">Negative</div>
            </div>
            <div class="sentiment-column">
                <div class="sentiment-value">{neutral_count}</div>
                <div class="sentiment-bar-area">
                    <div class="sentiment-bar neutral-bar" style="height:{neutral_height}px;"></div>
                </div>
                <div class="sentiment-label">Neutral</div>
            </div>
            <div class="sentiment-column">
                <div class="sentiment-value">{positive_count}</div>
                <div class="sentiment-bar-area">
                    <div class="sentiment-bar positive-bar" style="height:{positive_height}px;"></div>
                </div>
                <div class="sentiment-label">Positive</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.info("No customer reviews available yet.")

st.markdown('<div class="section-title">Customer Feedback</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    search_text = st.text_input("Search reviews", placeholder="Search by review text...")

with col2:
    sentiment_filter = st.selectbox("Filter by sentiment", ["All", "Positive", "Neutral", "Negative"])

filtered_df = reviews_df.copy()

if search_text:
    filtered_df = filtered_df[
        filtered_df["review"].fillna("").str.contains(search_text, case=False, na=False)
    ]

if sentiment_filter != "All":
    filtered_df = filtered_df[filtered_df["sentiment"] == sentiment_filter]

st.caption(f"Showing {len(filtered_df)} review(s)")

if sentiment_filter == "All":
    positive_reviews = filtered_df[filtered_df["sentiment"] == "Positive"]
    neutral_reviews = filtered_df[filtered_df["sentiment"] == "Neutral"]
    negative_reviews = filtered_df[filtered_df["sentiment"] == "Negative"]

    with st.expander(f"🟢 Positive Reviews ({len(positive_reviews)})"):
        if len(positive_reviews) > 0:
            st.dataframe(
                positive_reviews[["review","rating","created_at"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No positive reviews found.")

    with st.expander(f"⚪ Neutral Reviews ({len(neutral_reviews)})"):
        if len(neutral_reviews) > 0:
            st.dataframe(
                neutral_reviews[["review","rating","created_at"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No neutral reviews found.")

    with st.expander(f"🔴 Negative Reviews ({len(negative_reviews)})"):
        if len(negative_reviews) > 0:
            st.dataframe(
                negative_reviews[["review","rating","created_at"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No negative reviews found.")
else:
    if len(filtered_df) > 0:
        st.dataframe(
            filtered_df[["review","sentiment","rating","created_at"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No reviews match the selected filter.")

st.markdown('<div class="section-title">Model Performance</div>', unsafe_allow_html=True)

if accuracy is not None and report is not None:
    weighted_f1 = report["weighted avg"]["f1-score"]
    test_messages = int(report["weighted avg"]["support"])

    col1, col2, col3, col4 = st.columns(4)
    model_metrics = [
        ("Dataset", "300"),
        ("Test Messages", str(test_messages)),
        ("Accuracy", f"{accuracy * 100:.2f}%"),
        ("Weighted F1", f"{weighted_f1:.2f}")
    ]

    for col, (label, value) in zip([col1, col2, col3, col4], model_metrics):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',
                unsafe_allow_html=True
            )
else:
    st.info("Model evaluation data is not available yet.")

st.markdown('<div class="section-title">Classification Report</div>', unsafe_allow_html=True)

if report is not None:
    report_data = pd.DataFrame({
        "Sentiment": ["Negative", "Neutral", "Positive"],
        "Precision": [
            report["Negative"]["precision"],
            report["Neutral"]["precision"],
            report["Positive"]["precision"]
        ],
        "Recall": [
            report["Negative"]["recall"],
            report["Neutral"]["recall"],
            report["Positive"]["recall"]
        ],
        "F1 Score": [
            report["Negative"]["f1-score"],
            report["Neutral"]["f1-score"],
            report["Positive"]["f1-score"]
        ],
        "Support": [
            report["Negative"]["support"],
            report["Neutral"]["support"],
            report["Positive"]["support"]
        ]
    })
    st.dataframe(report_data, use_container_width=True, hide_index=True)
else:
    st.info("Classification report is not available yet.")

st.markdown('<div class="section-title">Confusion Matrix</div>', unsafe_allow_html=True)

if confusion is not None:
    st.dataframe(confusion, use_container_width=True)
else:
    st.info("Confusion matrix is not available yet.")

st.markdown(
    '<div class="section-title">VADER vs TF-IDF + Logistic Regression</div>',
    unsafe_allow_html=True
)

if os.path.exists(COMPARISON_PATH):
    comparison_df = pd.read_csv(COMPARISON_PATH)
    st.dataframe(
        comparison_df[[
            "message",
            "vader_score",
            "vader_sentiment",
            "ml_prediction",
            "match"
        ]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Comparison results are not available yet.")

st.markdown('<div class="section-title">Model Information</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="info-card">
            <b>Baseline</b><br>
            VADER Lexicon<br><br>
            <b>ML Algorithm</b><br>
            Logistic Regression<br><br>
            <b>Feature Extraction</b><br>
            TF-IDF
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="info-card">
            <b>Dataset</b><br>
            300 customer messages<br><br>
            <b>Training Data</b><br>
            240 messages<br><br>
            <b>Testing Data</b><br>
            60 messages
        </div>
        """,
        unsafe_allow_html=True
    )