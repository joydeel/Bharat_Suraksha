import streamlit as st
import google.generativeai as genai

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Bharat Suraksha AI", page_icon="🛡️")

# 2. TIRANGA THEME CSS (Saffron, White, Green)
st.markdown("""
    <style>
    /* Saffron Top Border */
    .stApp {
        border-top: 15px solid #FF9933;
        background-color: #FFFFFF;
    }
    
    /* Green Bottom Border */
    .main .block-container::after {
        content: "";
        display: block;
        height: 15px;
        background-color: #138808;
        width: 100%;
        position: fixed;
        bottom: 0;
        left: 0;
        z-index: 999;
    }

    /* Ashoka Chakra Blue Headers */
    h1, h2, h3 {
        color: #000080 !important;
        text-align: center;
    }

    /* Professional Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
        border-right: 2px solid #000080;
    }

    /* Blue "Action" Buttons */
    div.stButton > button:first-child {
        background-color: #000080;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        height: 3em;
    }

    /* Red "Emergency" Button for 1930 */
    div.stButton > button[kind="secondary"] {
        background-color: #FF0000;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. AI CONFIGURATION
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Key not found. Please add it to Streamlit Secrets.")

# 4. APP INTERFACE
st.title("🛡️ Bharat Suraksha AI")
st.write("### *Protecting India from Digital Scams*")

st.sidebar.image("https://img.icons8.com/color/96/shield-with-crown.png")
st.sidebar.title("App Menu")
st.sidebar.info("This AI analyzes the 'Dharma' (intent) of messages to detect fraud.")

# User Input
user_input = st.text_area("Paste the suspicious message, SMS, or WhatsApp text here:", height=150)

if st.button("🔍 SCAN FOR SCAMS"):
    if user_input:
        with st.spinner("Analyzing with Digital Dharma..."):
            prompt = f"Analyze this message for scams common in India. Is it a scam? Rate risk 0-100. Explain why in simple English and Hindi: {user_input}"
            response = model.generate_content(prompt)
            
            st.subheader("Analysis Result")
            st.info(response.text)
    else:
        st.warning("Please paste a message first!")

st.markdown("---")

# 5. EMERGENCY ACTION
st.subheader("🚨 Emergency Action")
col1, col2 = st.columns(2)

with col1:
    if st.button("Call 1930 Helpline"):
        st.write("📞 Dialing 1930...")
        st.markdown("[Click here to call 1930](tel:1930)")

with col2:
    if st.button("Report to Cybercrime.gov.in"):
        st.write("Redirecting to official portal...")
        st.markdown("[Visit Portal](https://cybercrime.gov.in)")

st.sidebar.write("---")
st.sidebar.write("🇮🇳 **Digital India Initiative 2026**")
