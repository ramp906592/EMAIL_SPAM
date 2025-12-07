import streamlit as st
import joblib
import re
import string
import numpy as np

# ---------------------------------------
# Load Model + Vectorizer
# ---------------------------------------
model = joblib.load("spam_model.pkl")
tfidf = joblib.load("tfidf_vectorizer.pkl")

# ---------------------------------------
# Clean Text Function
# ---------------------------------------
def clean_text(t):
    t = t.lower()
    t = re.sub(r"http\S+", " link ", t)
    t = t.translate(str.maketrans("", "", string.punctuation))
    t = re.sub(r"\d+", " number ", t)
    return t.strip()

# ---------------------------------------
# Streamlit UI Setup
# ---------------------------------------
st.set_page_config(page_title="AI Email Spam Detector", page_icon="📧", layout="wide")

# Sidebar
st.sidebar.title("📌 About the App")
st.sidebar.info("""
This AI model can detect:
- ✔ Phishing Emails  
- ✔ Job Scams  
- ✔ Fake Bank Alerts  
- ✔ Malicious Links  
- ✔ Lottery / Prize Scams  

Upload or paste any email text to check if it is spam or safe.
""")

# Main Title
st.markdown("<h1 style='text-align: center;'>📧 AI Email Spam / Phishing Detector</h1>", unsafe_allow_html=True)
st.write("### Paste your email below:")

email_text = st.text_area("", height=250, placeholder="Paste the email text here...")

# ---------------------------------------
# Prediction Logic
# ---------------------------------------
if st.button("🔍 Analyze Email"):
    if len(email_text.strip()) == 0:
        st.warning("⚠ Please paste an email to analyze!")
    else:
        cleaned = clean_text(email_text)
        vector = tfidf.transform([cleaned])
        pred = model.predict(vector)[0]

        # If model provides decision function / probability
        try:
            decision_score = model.decision_function(vector)[0]
            prob = 1 / (1 + np.exp(-decision_score))  
        except:
            prob = 0.85 if pred == 1 else 0.15

        # Show results
        if pred == 1:
            st.error("🚨 **Spam / Phishing Detected**")
            st.write("The email contains patterns commonly seen in scam or phishing messages.")

            st.progress(float(prob))  
            st.write(f"**Spam Probability:** `{prob*100:.2f}%`")
        else:
            st.success("✔️ **This Email Appears Safe**")

            st.progress(float(prob))
            st.write(f"**Safety Confidence:** `{(1-prob)*100:.2f}%`")

        # Highlight links inside email
        links_found = re.findall(r'(https?://[^\s]+)', email_text)
        if links_found:
            st.write("### 🔗 Links found inside email:")
            for link in links_found:
                st.write(f"- {link}")
