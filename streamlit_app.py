import streamlit as st
import google.generativeai as genai

st.title("🛡️ Bharat Suraksha AI")
st.subheader("Digital Dharma Scam Protection")

# Connect to your Gemini API
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

msg = st.text_area("Paste suspicious message:")
if st.button("Analyze Intent"):
    response = model.generate_content(f"Is this an Indian scam? Explain in Hindi & English: {msg}")
    st.write(response.text)
    st.button("🚨 Call 1930 Helpline")
st.sidebar.title("📖 How it Works")
st.sidebar.info("1. Copy scam text\n2. AI checks 'Dharma' (Intent)\n3. Get Risk Score")

st.sidebar.title("📖 How it Works")
st.sidebar.info("1. Copy scam text\n2. AI checks 'Dharma' (Intent)\n3. Get Risk Score")

