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

st.sidebar.title("📖 How it Works")
st.sidebar.info("1. Copy scam text\n2. AI checks 'Dharma' (Intent)\n3. Get Risk Score")
import streamlit as st

# --- TIRANGA THEME CSS ---
st.markdown("""
    <style>
    /* Main Background and Top Border (Saffron) */
    .stApp {
        border-top: 15px solid #FF9933;
        background-color: #FFFFFF;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 2px solid #138808;
    }

    /* Buttons (Ashoka Chakra Navy Blue) */
    div.stButton > button:first-child {
        background-color: #000080;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    
    /* Button Hover Effect */
    div.stButton > button:first-child:hover {
        background-color: #FF9933;
        color: white;
        border: 2px solid #000080;
    }

    /* Footer Border (Green) */
    footer {
        visibility: hidden;
    }
    .main .block-container::after {
        content: "";
        display: block;
        height: 15px;
        background-color: #138808;
        width: 100%;
        position: fixed;
        bottom: 0;
        left: 0;
    }
    
    /* Heading Color */
    h1, h2, h3 {
        color: #000080 !important;
    }
    </style>
    """, unsafe_allow_html=True)
