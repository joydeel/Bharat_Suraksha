import json
import re
import time
import math
from typing import Any, Dict, Optional

import numpy as np
import streamlit as st
import google.generativeai as genai

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(page_title="Bharat Suraksha — CyberSecure", page_icon="🛡️", layout="wide")

# ---------------------------
# Neon-Glass + Ashoka Chakra CSS (Glassmorphism + animated chakra)
# ---------------------------
st.markdown(
    """
    <style>
    :root{
        --neon-saffron: #FF9933;
        --neon-green: #39FF14;
        --glass-bg: rgba(10,12,20,0.45);
        --glass-border: rgba(255,255,255,0.06);
        --accent-blue: #0ea5ff;
    }
    /* Page bg */
    .stApp {
        background: radial-gradient(ellipse at top left, #071025 0%, #020617 60%);
        color: #e9f2ff;
    }
    /* Glass card */
    .glass {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border: 1px solid var(--glass-border);
        border-radius: 14px;
        padding: 18px;
        backdrop-filter: blur(8px) saturate(130%);
        box-shadow: 0 6px 30px rgba(0,0,0,0.6);
    }
    /* Neon buttons */
    .neon {
        background: linear-gradient(90deg, var(--neon-saffron), var(--neon-green));
        color: #081010 !important;
        border-radius: 10px;
        padding: 8px 12px;
        font-weight: 700;
    }
    .neon:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(255,153,51,0.12); }
    /* Badge for results */
    .badge {
        padding: 10px;
        border-radius: 8px;
        font-weight: 800;
        text-align: center;
        color: #001010;
    }
    /* Ashoka Chakra animation */
    .chakra {
        width: 68px;
        height: 68px;
        margin: 0 auto 8px auto;
        border-radius: 50%;
        border: 4px solid rgba(255,255,255,0.06);
        position: relative;
        box-shadow: 0 0 18px rgba(57,255,20,0.02);
        animation: spin 2.6s linear infinite;
    }
    .chakra:after{
        content: '';
        position: absolute;
        inset: 9px;
        border-radius: 50%;
        border: 4px dashed rgba(255,153,51,0.18);
    }
    @keyframes spin { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
    /* Responsive tweaks */
    @media (max-width: 640px) {
        .glass { padding: 12px; border-radius: 10px; }
    }
    /* Progress bar style */
    .stProgress > div > div > div > div { background: linear-gradient(90deg, var(--neon-saffron), var(--neon-green)) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Universal language dictionary
# ---------------------------
LANG = {
    "English": {
        "title": "🛡️ Bharat Suraksha — Cyber Secure",
        "subtitle": "Detecting social engineering, phishing & scams across Indian contexts",
        "paste_prompt": "Paste the suspicious message, SMS, or WhatsApp text here:",
        "scan_button": "🔍 Analyze (Deep Intent)",
        "analysis_result": "Analysis Result",
        "analyzing_superposition": "Analyzing Superposition (Quantum Digital Dharma)...",
        "please_paste": "Please paste a message first!",
        "emergency_action": "🚨 Emergency Actions",
        "call_1930": "Call 1930 Helpline",
        "report_cyber": "Report to Cybercrime.gov.in",
        "report_chakshu": "Report to Chakshu (Sanchar Saathi)",
        "chakshu_cta": "Report forged KYC / SIM / SMS scams to Sanchar Saathi",
        "raw_response": "Raw model response",
        "upload_key": "User Gemini API Key (session only)",
        "use_app_key": "Use app-level key from Streamlit Secrets",
        "login": "Sign in (simulated)",
        "logout": "Sign out",
        "quantum_result": "Quantum collapse indicates:",
        "safe": "SAFE",
        "scam": "SCAM",
        "unknown": "SUSPECT",
        "social_tactics": "Social Engineering Tactics detected",
        "matched_patterns": "Matched patterns",
    },
    "Hindi": {
        "title": "🛡️ भारत सुरक्षा — साइबर सुरक्षित",
        "subtitle": "सोशल इंजीनियरिंग, फ़िशिंग और भारतीय संदर्भों में स्कैम का पता लगाएँ",
        "paste_prompt": "संदेहास्पद संदेश, SMS या WhatsApp टेक्स्ट यहाँ पेस्ट करें:",
        "scan_button": "🔍 विश्लेषण (डीप इंटेंट)",
        "analysis_result": "विश्लेषण परिणाम",
        "analyzing_superposition": "सुपरपोजीशन विश्लेषण (क्वांटम डिजिटल धर्मा)...",
        "please_paste": "कृपया पहले एक संदेश पेस्ट करें!",
        "emergency_action": "🚨 आपातकालीन क्रियाएँ",
        "call_1930": "1930 हेल्पलाइन कॉल करें",
        "report_cyber": "Cybercrime.gov.in पर रिपोर्ट करें",
        "report_chakshu": "Chakshu (Sanchar Saathi) को रिपोर्ट करें",
        "chakshu_cta": "नकली KYC / SIM / SMS स्कैम Sanchar Saathi पर रिपोर्ट करें",
        "raw_response": "कच्ची मॉडल प्रतिक्रिया",
        "upload_key": "User Gemini API Key (सिर्फ सत्र के लिए)",
        "use_app_key": "Streamlit Secrets से ऐप-स्तरीय कुंजी का उपयोग करें",
        "login": "साइन इन (नकली)",
        "logout": "साइन आउट",
        "quantum_result": "क्वांटम कोलैप्स बताता है:",
        "safe": "सुरक्षित",
        "scam": "ठगाई",
        "unknown": "संदिग्ध",
        "social_tactics": "पाए गए सोशल इंजीनियरिंग रणनीतियाँ",
        "matched_patterns": "मिलते पैटर्न",
    },
    "Bengali": {
        "title": "🛡️ Bharat Suraksha — সাইবার সিকিউর",
        "subtitle": "সামাজিক প্রকৌশল, ফিশিং এবং ভারতীয় স্ক্যাম সনাক্তকরণ",
        "paste_prompt": "সন্দেহপূর্ণ বার্তা, SMS বা WhatsApp টেক্সট এখানে পেস্ট করুন:",
        "scan_button": "🔍 বিশ্লেষণ (গভীর অভিপ্রায়)",
        "analysis_result": "বিশ্লেষণ ফলাফল",
        "analyzing_superposition": "সুপারপজিশন বিশ্লেষণ (কোয়ান্টাম ডিজিটাল ধর্মা)...",
        "please_paste": "অনুগ্রহ করে প্রথমে একটি বার্তা পেস্ট করুন!",
        "emergency_action": "🚨 জরুরি কর্ম",
        "call_1930": "1930 হেল্পলাইন কল করুন",
        "report_cyber": "Cybercrime.gov.in-এ রিপোর্ট করুন",
        "report_chakshu": "Chakshu-এ রিপোর্ট করুন (Sanchar Saathi)",
        "chakshu_cta": "নকল KYC / SIM / SMS স্ক্যাম Sanchar Saathi-এ রিপোর্ট করুন",
        "raw_response": "র ড মডেল প্রতিক্রিয়া",
        "upload_key": "User Gemini API Key (শুধু সেশন)",
        "use_app_key": "Streamlit Secrets থেকে অ্যাপ-কী ব্যবহার করুন",
        "login": "সাইন ইন (নক্সিক)",
        "logout": "সাইন আউট",
        "quantum_result": "কোয়ান্টাম পতন নির্দেশ করে:",
        "safe": "নিরাপদ",
        "scam": "ঠোকাঠাক",
        "unknown": "সন্দেহজনক",
        "social_tactics": "কী সামাজিক প্রকৌশল কৌশলগুলি সনাক্ত হয়েছে",
        "matched_patterns": "মেলানো প্যাটার্ন",
    },
    "Tamil": {
        "title": "🛡️ Bharat Suraksha — சைபர் பாதுகாப்பு",
        "subtitle": "சமூக பொறியியல், பிஷிங் மற்றும் இந்திய மோசடிகளை கண்டறிதல்",
        "paste_prompt": "சந்தேகமான செய்தி, SMS அல்லது WhatsApp உரையை இங்கே ஒட்டவும்:",
        "scan_button": "🔍 分析 (ஆழமான நோக்கம்)",
        "analysis_result": "விசாரணை முடிவு",
        "analyzing_superposition": "சூப்பர்போசிஷன் ஆய்வு (குவாண்டம் டிஜிட்டல் தர்மா)...",
        "please_paste": "தயவு செய்து முதலில் ஒரு செய்தியை ஒட்டவும்!",
        "emergency_action": "🚨 அவசர நடவடிக்கைகள்",
        "call_1930": "1930 ஹெல்ப்லைன் அழைக்கவும்",
        "report_cyber": "Cybercrime.gov.in-க்கு புகார் செய்யவும்",
        "report_chakshu": "Chakshu-க்கு புகார் செய்யவும் (Sanchar Saathi)",
        "chakshu_cta": "மோசடியான KYC / SIM / SMS மோசடிகளை Sanchar Saathi-க்கு புகார் செய்யவும்",
        "raw_response": "உறுதிப்படுத்தாத மாதிரி பதில்",
        "upload_key": "User Gemini API Key (சேஷன் மட்டுமே)",
        "use_app_key": "Streamlit Secrets இல் இருந்து செயலி-முக்கியத்தைப் பயன்படுத்தவும்",
        "login": "உள்நுழைக (தற்காலிக)",
        "logout": "வெளியேறு",
        "quantum_result": "குவாண்டம் சரிவால் காட்டப்படுவது:",
        "safe": "பாதுகாப்பானது",
        "scam": "மோசடி",
        "unknown": "இணைக்கபட்டது",
        "social_tactics": "கட்டமைப்பு கண்டறியப்பட்ட சமூக பொறியியல் மோசடிகள்",
        "matched_patterns": "பட்டர்ன்கள்",
    },
    "Telugu": {
        "title": "🛡️ Bharat Suraksha — సైబర్ సెక్యూర్",
        "subtitle": "సామాజిక ఇంజినీరింగ్, ఫిషింగ్ మరియు భారతీయ స్కామ్‌ల గుర్తింపు",
        "paste_prompt": "సందేహాస్పద సందేశం, SMS లేదా WhatsApp వచనం ఇక్కడ పేస్ట్ చేయండి:",
        "scan_button": "🔍 విశ్లేషణ (డీప్ ఇన్టెంట్)",
        "analysis_result": "విశ్లేషణ ఫలితం",
        "analyzing_superposition": "సూపర్ఫోజిషన్ విశ్లేషణ (క్వాంటమ్ డిజిటల్ ధర్మా)...",
        "please_paste": "దయచేసి మొదట ఒక సందేశాన్ని పేస్ట్ చేయండి!",
        "emergency_action": "🚨 అత్యవసర చర్యలు",
        "call_1930": "1930 హెల్ప్‌లైన్��కు కాల్ చేయండి",
        "report_cyber": "Cybercrime.gov.inకి నివేదించండి",
        "report_chakshu": "Chakshuకి నివేదించండి (Sanchar Saathi)",
        "chakshu_cta": "నకిలీ KYC / SIM / SMS స్కామ్‌లను Sanchar Saathiలో నివేదించండి",
        "raw_response": "రా మోడల్ ప్రతిస్పందన",
        "upload_key": "User Gemini API Key (సెషన్ మాత్రమే)",
        "use_app_key": "Streamlit Secrets నుండి యాప్-స్థాయి కీ ఉపయోగించండి",
        "login": "సైన్ ఇన్ (నకిలీ)",
        "logout": "సైన్ అవుట్",
        "quantum_result": "క్వాంటమ్ కollapse ఫలితం:",
        "safe": "సురక్షితం",
        "scam": "ఐన నకిలీ",
        "unknown": "సందేహాస్పదం",
        "social_tactics": "పాల్సిన సోషియల్ ఇంజినీరింగ్ తంత్రాలు",
        "matched_patterns": "మ్యాచ్డ్ ప్యాటర్న్‌లు",
    },
}

# ---------------------------
# Session state initialization
# ---------------------------
def init_state():
    defaults = {
        "language": "English",
        "last_input": "",
        "last_parsed": None,
        "last_score": None,
        "user_api_key": None,
        "logged_in_user": None,
        "quantum_result": None,
        "is_processing": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()

# ---------------------------
# Helper: Simulated login (placeholder)
# ---------------------------
def login_placeholder(labels: Dict[str, str]) -> None:
    """
    Simulated login UI: sets st.session_state['logged_in_user'] to a fake value.
    Replace with proper OAuth server-side flow in production.
    """
    if st.session_state.get("logged_in_user"):
        st.sidebar.markdown(f"**User:** {st.session_state['logged_in_user']}")
        if st.sidebar.button(labels["logout"]):
            st.session_state["logged_in_user"] = None
            st.sidebar.success("Signed out")
    else:
        if st.sidebar.button(labels["login"]):
            # simulate sign in for demo; in prod implement proper OAuth
            st.session_state["logged_in_user"] = "user@example.com"
            st.sidebar.success("Signed in as user@example.com")


# ---------------------------
# API key selection logic (priority)
# ---------------------------
def effective_api_key() -> Optional[str]:
    """
    Priority:
      1. st.session_state['user_api_key'] (session-only, if provided)
      2. st.secrets['GOOGLE_API_KEY'] (app-level secret)
    """
    user_key = st.session_state.get("user_api_key")
    if user_key:
        return user_key
    return st.secrets.get("GOOGLE_API_KEY") if "GOOGLE_API_KEY" in st.secrets else None


# ---------------------------
# Model configuration with error handling
# ---------------------------
def configure_model(api_key: Optional[str]):
    """
    Configure google.generativeai safely. Returns a GenerativeModel instance or None.
    """
    if not api_key:
        st.error("No API key available. Add GOOGLE_API_KEY to Streamlit Secrets or provide a per-session key.")
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        st.error("Failed to configure GenAI client. Check key or network.")
        # Do not reveal keys or stack traces to users; show minimal message.
        return None


# ---------------------------
# Advanced Forensic AI prompt builder
# ---------------------------
def build_deep_intent_prompt(message: str, language: str) -> str:
    """
    Build a 'Deep Intent Analysis' prompt instructing Gemini to act as a Digital Forensic Investigator.
    Instructs returning a strict JSON object with fields:
      is_scam: yes|no|suspect
      score: int 0-100
      explanations: {"en": "...", "hi": "...", ...} (if possible)
      social_engineering_tactics: [ "urgency", "authority", "fear", "phishing", ... ]
      matched_patterns: [...]
    """
    patterns = [
        "electricity bill disconnected",
        "KYC expiry",
        "WhatsApp job offer",
        "bank OTP request",
        "refund / payment due",
        "lottery / prize",
        "fake URL / short link",
        "request to install an app or share KYC"
    ]
    pattern_text = "; ".join(patterns)
    prompt = f"""
You are a Digital Forensic Investigator specialized in scams in India. Analyze the following message for intent and social engineering tactics.
Return ONLY a JSON object (no explanation text) with these fields:
- is_scam: "yes"|"no"|"suspect"
- score: integer 0-100 (100 => certain scam)
- explanations: object with keys 'en' and 'hi' (English and Hindi concise explanations)
- social_engineering_tactics: array of tactics detected (e.g., "urgency", "authority", "pretexting", "fear", "phishing", "baiting")
- matched_patterns: array of pattern strings you matched (from known Indian tropes)

Look specifically for these tropes: {pattern_text}
Message: \"\"\"{message}\"\"\"

Ensure score is an integer and return valid JSON only.
"""
    return prompt


# ---------------------------
# Model call wrapper + robust parsing
# ---------------------------
def call_model_and_parse(model, prompt: str) -> Dict[str, Any]:
    """
    Call model.generate_content with defensive error handling.
    Try to extract JSON; fall back to safe heuristics.
    """
    raw_text = ""
    try:
        response = model.generate_content(prompt)
        # Extract text safely; the response object shape may vary by client version
        if hasattr(response, "text") and response.text:
            raw_text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            first = response.candidates[0]
            raw_text = getattr(first, "content", getattr(first, "text", str(first)))
        else:
            raw_text = str(response)
    except Exception as e:
        # Keep error minimal for user, but include fallback raw JSON for debug
        err_msg = {"error": "model_call_failed", "message": str(e)}
        raw_text = json.dumps(err_msg)
        st.error("AI call failed — showing conservative fallback.")
    parsed = parse_model_response(raw_text)
    parsed["raw"] = raw_text
    return parsed


def parse_model_response(text: str) -> Dict[str, Any]:
    """
    Parse the model's JSON response if possible. If not, attempt regex heuristics.
    Returns normalized dictionary with defaults.
    """
    try:
        data = json.loads(text)
        is_scam = data.get("is_scam", "suspect")
        score = int(data.get("score", 50))
        explanations = data.get("explanations", {})
        tactics = data.get("social_engineering_tactics", [])
        matched = data.get("matched_patterns", [])
        return {
            "is_scam": is_scam,
            "score": max(0, min(100, score)),
            "explanations": explanations,
            "tactics": tactics,
            "matched_patterns": matched,
            "raw": text,
        }
    except Exception:
        # Fallback heuristics
        score = 50
        m = re.search(r"(\b[0-9]{1,3}\b)\s*(%|percent)?", text)
        if m:
            try:
                c = int(m.group(1))
                if 0 <= c <= 100:
                    score = c
            except:
                pass
        is_scam = "suspect"
        if re.search(r"\b(scam|fraud|fake|malicious|phish)\b", text, re.I):
            is_scam = "yes"
        elif re.search(r"\b(safe|benign|not a scam|trustworthy)\b", text, re.I):
            is_scam = "no"
        # naive pattern detection
        known = ["electricity", "bill", "KYC", "job", "WhatsApp", "OTP", "link", "refund", "lottery", "prize", "UPI"]
        matched = [p for p in known if re.search(p, text, re.I)]
        return {
            "is_scam": is_scam,
            "score": score,
            "explanations": {"en": text},
            "tactics": [],
            "matched_patterns": matched,
            "raw": text,
        }


# ---------------------------
# Quantum Digital Dharma Engine (qubit simulation)
# ---------------------------
def hadamard_matrix():
    return (1 / math.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)


def simulate_qubit_and_collapse(model_score: int, progress_callback=None, steps: int = 20, sleep_per_step: float = 0.03):
    """
    Simulate qubit |ψ> = α|0> + β|1> where |β|^2 ~= model_score/100.
    - Show an 'Analyzing Superposition' progress via progress_callback (if provided).
    - Apply Hadamard to generate superposition (visualized).
    - Collapse (measure) using resulting probabilities.
    Returns a dict with amplitudes, probabilities, and measured outcome (0 safe, 1 scam).
    """
    # Map model score to initial probability of |1> (scam)
    p1 = np.clip(model_score / 100.0, 0.0, 1.0)
    a0 = math.sqrt(max(0.0, 1 - p1))
    a1 = math.sqrt(max(0.0, p1))
    state = np.array([a0, a1], dtype=complex).reshape(2, 1)

    # Animate progress bar (if callback provided)
    if progress_callback:
        for i in range(steps):
            progress_callback((i + 1) / steps)
            time.sleep(sleep_per_step)

    # Apply Hadamard
    H = hadamard_matrix()
    superposed = H @ state
    probs = np.abs(superposed.flatten()) ** 2
    probs = probs / probs.sum()

    # Random measurement
    measured = np.random.choice([0, 1], p=[float(probs[0]), float(probs[1])])
    return {
        "initial_amplitudes": [float(round(a0, 4)), float(round(a1, 4))],
        "superposed_amplitudes": [float(round(superposed[0].real, 4)), float(round(superposed[1].real, 4))],
        "probabilities": [float(round(probs[0], 4)), float(round(probs[1], 4))],
        "measured": int(measured),
    }


# ---------------------------
# Risk label/color mapping
# ---------------------------
def risk_label_color(score: int):
    if score <= 33:
        return LANG[st.session_state["language"]]["safe"], "#39FF14"  # Neon green
    elif score <= 66:
        return LANG[st.session_state["language"]]["unknown"], "#FFD700"  # Golden-ish
    else:
        return LANG[st.session_state["language"]]["scam"], "#FF9933"  # Neon saffron


# ---------------------------
# UI: Sidebar controls (language, login, API key)
# ---------------------------
def sidebar_controls():
    # Language toggle
    lang = st.sidebar.selectbox("Language / भाषा", list(LANG.keys()), index=list(LANG.keys()).index(st.session_state["language"]))
    st.session_state["language"] = lang
    labels = LANG[lang]

    st.sidebar.markdown("---")
    # Simulated login
    login_placeholder(labels)

    st.sidebar.markdown("### API Key (session)")
    if st.session_state.get("logged_in_user"):
        # If logged in, allow user to paste a per-session API key (stored only in session_state)
        key = st.sidebar.text_input(labels["upload_key"], type="password", value=st.session_state.get("user_api_key") or "")
        if key:
            st.session_state["user_api_key"] = key.strip()
            st.sidebar.success("Key stored for this session only.")
        use_app = st.sidebar.checkbox(labels["use_app_key"], value=not bool(st.session_state.get("user_api_key")))
        if use_app:
            st.session_state["user_api_key"] = None
    else:
        st.sidebar.info("Sign in to provide a per-session API key.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Resources")
    st.sidebar.markdown(f"- [Cybercrime Portal](https://cybercrime.gov.in)")
    st.sidebar.markdown(f"- [Sanchar Saathi (DoT)](https://sancharsaathi.gov.in)")


# ---------------------------
# Main analysis flow + UI
# ---------------------------
def run_analysis():
    labels = LANG[st.session_state["language"]]

    # Title card
    st.markdown(f"<div class='glass'><h1 style='margin-bottom:6px'>{labels['title']}</h1><p style='margin-top:0;color:#cfe9ff'>{labels['subtitle']}</p></div>", unsafe_allow_html=True)
    st.write("")

    left, right = st.columns([2, 1])

    with left:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        user_text = st.text_area(labels["paste_prompt"], value=st.session_state.get("last_input", ""), height=170)
        st.session_state["last_input"] = user_text
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button(labels["scan_button"]):
            if not user_text:
                st.warning(labels["please_paste"])
            else:
                # Begin processing
                st.session_state["is_processing"] = True
                api_key = effective_api_key()
                model = configure_model(api_key)
                if not model:
                    st.error("AI model unavailable. Check API key.")
                    st.session_state["is_processing"] = False
                    return

                # Build prompt and call model
                prompt = build_deep_intent_prompt(user_text, st.session_state["language"])
                # Show Ashoka Chakra animation while calling model (visual)
                with st.spinner("Contacting forensic AI..."):
                    parsed = call_model_and_parse(model, prompt)

                # Keep parsed and score in session
                st.session_state["last_parsed"] = parsed
                st.session_state["last_score"] = parsed.get("score", 50)

                # Quantum superposition animation: progressive collapse
                st.markdown("<div style='text-align:center'><div class='chakra'></div></div>", unsafe_allow_html=True)
                prog = st.progress(0)
                qres = simulate_qubit_and_collapse(st.session_state["last_score"], progress_callback=prog.progress, steps=30, sleep_per_step=0.03)
                st.session_state["quantum_result"] = qres
                st.session_state["is_processing"] = False

                # Render results
                render_results(parsed, qres)

        # If previous results exist, show them (persistent across language toggle)
        elif st.session_state.get("last_parsed"):
            parsed = st.session_state["last_parsed"]
            qres = st.session_state.get("quantum_result")
            if not qres:
                # Simulate a quantum run for display if not present
                prog = st.progress(0)
                qres = simulate_qubit_and_collapse(parsed.get("score", 50), progress_callback=prog.progress, steps=20, sleep_per_step=0.02)
                st.session_state["quantum_result"] = qres
            render_results(parsed, qres)

    with right:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### Session & Actions")
        if st.session_state.get("logged_in_user"):
            st.markdown(f"- Signed in as **{st.session_state['logged_in_user']}**")
        else:
            st.markdown("- Not signed in (use Sign in in sidebar)")

        # Do NOT display API keys; only show whether user key is present
        if st.session_state.get("user_api_key"):
            st.markdown("- Per-session API key: **Provided**")
        else:
            st.markdown("- Per-session API key: **Not provided** (using app-level key if available)")

        st.markdown("---")
        st.markdown(f"### {labels['emergency_action']}")
        if st.button(labels["call_1930"]):
            st.write("📞 Dialing 1930...")
            st.markdown("[Click here to call 1930](tel:1930)")
        if st.button(labels["report_cyber"]):
            st.write("Redirecting to official portal...")
            st.markdown("[Visit Portal](https://cybercrime.gov.in)")
        st.markdown("---")
        st.markdown(f"### {labels['report_chakshu']}")
        st.markdown(labels["chakshu_cta"])
        st.markdown("[Report on Sanchar Saathi (DoT)](https://sancharsaathi.gov.in)")
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# Render analysis results
# ---------------------------
def render_results(parsed: Dict[str, Any], qres: Dict[str, Any]):
    labels = LANG[st.session_state["language"]]
    st.markdown("<div class='glass' style='margin-top:12px'>", unsafe_allow_html=True)
    st.markdown(f"## {labels['analysis_result']}")

    score = int(parsed.get("score", 50))
    label, color = risk_label_color(score)

    # Visual meter
    st.progress(score / 100)

    # Badge
    st.markdown(f"<div class='badge' style='background:{color};'>{label} — Risk Score: {score}%</div>", unsafe_allow_html=True)

    # Quantum outcome
    measured = qres.get("measured", 0) if qres else 0
    measurement_text = labels["scam"] if measured == 1 else labels["safe"]
    st.markdown(f"**{labels['quantum_result']}** {measurement_text}")

    # Qubit details
    if qres:
        st.write("Initial amplitudes (|0>, |1>):", qres["initial_amplitudes"])
        st.write("Superposed amplitudes:", qres["superposed_amplitudes"])
        st.write("Probabilities (|0>, |1>):", qres["probabilities"])

    # Patterns & tactics
    matched = parsed.get("matched_patterns") or []
    tactics = parsed.get("tactics") or parsed.get("social_engineering_tactics") or []
    st.markdown(f"**{labels['matched_patterns']}:** " + (", ".join(matched) if matched else "None"))
    st.markdown(f"**{labels['social_tactics']}:** " + (", ".join(tactics) if tactics else "None"))

    # Explanation: prefer language-specific explanation if available
    explanations = parsed.get("explanations", {}) or {}
    lang_code = st.session_state["language"][:2].lower()
    explanation_text = explanations.get(lang_code) or explanations.get("en") or parsed.get("raw", "")
    st.markdown("**Explanation:**")
    st.write(explanation_text)

    # Raw response (collapsible for auditors)
    with st.expander(labels["raw_response"]):
        st.code(parsed.get("raw", ""))

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# Entry point
# ---------------------------
def main():
    sidebar_controls()
    run_analysis()


if __name__ == "__main__":
    main()
