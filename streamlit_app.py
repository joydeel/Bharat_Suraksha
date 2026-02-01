import json
import re
import math
import numpy as np
from typing import Any, Dict, Optional

import streamlit as st
import google.generativeai as genai

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="Bharat Suraksha AI — Cyber Secure", page_icon="🛡️", layout="wide")

# -----------------------
# GLASSMORPHISM + THEME CSS
# -----------------------
st.markdown(
    """
    <style>
    :root{
        --glass-bg: rgba(255,255,255,0.03);
        --glass-border: rgba(255,255,255,0.06);
        --neon-saffron: #FF9933;
        --neon-green: #39FF14;
        --accent-blue: #00bcd4;
    }
    /* Page background */
    .stApp {
        background: linear-gradient(180deg,#020617 0%, #0b1020 100%);
        color: #e6eef8;
    }
    /* Glass card */
    .glass {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border: 1px solid var(--glass-border);
        backdrop-filter: blur(8px) saturate(140%);
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 6px 30px rgba(0,0,0,0.5);
    }
    /* Neon accents */
    .neon-btn {
        background: linear-gradient(90deg, var(--neon-saffron), var(--neon-green));
        color: #001011 !important;
        border-radius: 10px;
        padding: 10px 14px;
        font-weight: 700;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
        box-shadow: 0 6px 18px rgba(57,255,20,0.06);
    }
    .neon-btn:hover{
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(255,153,51,0.12);
    }
    /* Buttons */
    div.stButton > button:first-child {
        width: 100%;
    }
    /* Small responsive tweaks */
    @media (max-width: 600px) {
        .glass { padding: 12px; border-radius: 10px; }
    }
    /* Progress bar color override */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--neon-saffron), var(--neon-green))!important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# MULTILINGUAL DICTIONARY
# -----------------------
MULTI = {
    "English": {
        "title": "🛡️ Bharat Suraksha AI — Cyber Secure",
        "subtitle": "Protecting India from social-engineering & digital scams",
        "paste_prompt": "Paste the suspicious message, SMS, or WhatsApp text here:",
        "scan_button": "🔍 Scan for Scams",
        "analysis_result": "Analysis Result",
        "emergency_action": "🚨 Emergency Action",
        "call_1930": "Call 1930 Helpline",
        "report_cyber": "Report to Cybercrime.gov.in",
        "report_chakshu": "Report to Chakshu (Sanchar Saathi)",
        "chakshu_cta": "Report forged KYC / SIM / SMS scams to Sanchar Saathi",
        "analyzing": "Analyzing with Digital Dharma...",
        "please_paste": "Please paste a message first!",
        "upload_key": "Provide your User Gemini API Key (session only)",
        "use_secrets": "Use app-level key from Streamlit Secrets",
        "quantum_title": "Quantum 'Digital Dharma' Simulation",
        "quantum_explain": "Superposition visualized; final result collapses combining AI confidence & quantum simulation.",
        "raw_response": "Raw model response (debug)",
        "login": "Sign in with Google (placeholder)",
        "logout": "Sign out"
    },
    "Hindi": {
        "title": "🛡️ भारत सुरक्षा AI — साइबर सिक्योर",
        "subtitle": "सोशल-इंजीनियरिंग और डिजिटल स्कैम से सुरक्षा",
        "paste_prompt": "संदेहास्पद संदेश, SMS, या WhatsApp टेक्स्ट यहाँ पेस्ट करें:",
        "scan_button": "🔍 स्कैम के लिए स्कैन करें",
        "analysis_result": "विश्लेषण परिणाम",
        "emergency_action": "🚨 आपातकालीन कार्रवाई",
        "call_1930": "1930 हेल्पलाइन कॉल करें",
        "report_cyber": "Cybercrime.gov.in पर रिपोर्ट करें",
        "report_chakshu": "Chakshu को रिपोर्ट करें (Sanchar Saathi)",
        "chakshu_cta": "नकली KYC / SIM / SMS स्कैम Sanchar Saathi पर रिपोर्ट करें",
        "analyzing": "डिजिटल धर्मा के साथ विश्लेषण कर रहे हैं...",
        "please_paste": "कृपया पहले एक संदेश पेस्ट करें!",
        "upload_key": "अपना User Gemini API Key प्रदान करें (केवल सत्र)",
        "use_secrets": "Streamlit Secrets से ऐप-स्तरीय कुंजी का उपयोग करें",
        "quantum_title": "क्वांटम 'डिजिटल धर्मा' सिमुलेशन",
        "quantum_explain": "सुपरपोजीशन दिखाएँ; अंतिम परिणाम AI आत्मविश्वास और क्वांटम सिमुलेशन को मिलाता है।",
        "raw_response": "कच्चा मॉडल प्रतिक्रिया (डिबग)"
    },
    "Bengali": {
        "title": "🛡️ Bharat Suraksha AI — সাইবার সুরক্ষা",
        "subtitle": "সামাজিক প্রকৌশল ও ডিজিটাল ঠকবাজি থেকে সুরক্ষা",
        "paste_prompt": "সন্দেহজনক বার্তা, SMS বা WhatsApp টেক্সট এখানে পেস্ট করুন:",
        "scan_button": "🔍 স্ক্যানে করুন",
        "analysis_result": "বিশ্লেষণ ফলাফল",
        "emergency_action": "🚨 জরুরি ক্রিয়া",
        "call_1930": "1930 হেল্পলাইন কল করুন",
        "report_cyber": "Cybercrime.gov.in-এ রিপোর্ট করুন",
        "report_chakshu": "Chakshu-এ রিপোর্ট করুন (Sanchar Saathi)",
        "chakshu_cta": "নকল KYC / SIM / SMS ঠকবাজি Sanchar Saathi-তে রিপোর্ট করুন",
        "analyzing": "ডিজিটাল ধর্মা দিয়ে বিশ্লেষণ চলছে...",
        "please_paste": "অনুগ্রহ করে প্রথমে একটি বার্তা পেস্ট করুন!",
        "upload_key": "আপনার User Gemini API Key প্রদান করুন (শুধু সেশন)",
        "use_secrets": "Streamlit Secrets থেকে অ্যাপ-স্তরের কী ব্যবহার করুন",
        "quantum_title": "কোয়ান্টাম 'ডিজিটাল ধর্মা' সিমুলেশন",
        "quantum_explain": "সুপারপজিশন দেখানো হচ্ছে; চূড়ান্ত ফলাফল AI আত্মবিশ্বাস এবং কোয়ান্টাম সিমুলেশনকে একত্রিত করে।",
        "raw_response": "কাঁচা মডেল প্রতিক্রিয়া (ডিবাগ)"
    },
    "Tamil": {
        "title": "🛡️ Bharat Suraksha AI — கையெழுத்து பாதுகாப்பு",
        "subtitle": "சமூக பொறியியல் மற்றும் டிஜிட்டல் மோசடிகளிலிருந்து பாதுகாப்பு",
        "paste_prompt": "சந்தேகமான செய்தி, SMS அல்லது WhatsApp உரையை இங்கே ஒட்டவும்:",
        "scan_button": "🔍 மோசடி சோதிக்கவும்",
        "analysis_result": "विश्लेषण முடிவு",
        "emergency_action": "🚨 அவசர நடவடிக்கை",
        "call_1930": "1930 ஹெல்ப்லைன் அழைப்பு",
        "report_cyber": "Cybercrime.gov.in-ல் புகார் செய்யவும்",
        "report_chakshu": "Chakshu-க்கு புகார் (Sanchar Saathi)",
        "chakshu_cta": "ஓகே KYC / SIM / SMS மோசடிகளை Sanchar Saathi-க்கு புகார் செய்யவும்",
        "analyzing": "டிஜிட்டல் தர்மா மூலம் பகுப்பாய்வு...",
        "please_paste": "முதலில் ஒரு செய்தியை ஒட்டவும்!",
        "upload_key": "உங்கள் User Gemini API Key வழங்கவும் (சேஷன் மட்டும்)",
        "use_secrets": "Streamlit Secrets இல் இருந்து செயலி-அளவிலான திறவுகோலைப் பயன்படுத்தவும்",
        "quantum_title": "குவாண்டம் 'டிஜிட்டல் தர்மா' சிமுலேஷன்",
        "quantum_explain": "அனிசித்தலை காட்டுகிறது; இறுதி முடிவு AI நம்பிக்கையும் குவாண்டம் சிமுலேஷனையும் ஒன்றிணைக்கிறது.",
        "raw_response": "அம்சப்பூர்வ ம��டல் பதில் (டைபக்)"
    },
    "Telugu": {
        "title": "🛡️ Bharat Suraksha AI — సైబర్ సెక్యూర్",
        "subtitle": "సోషల్ ఇంజినీరింగ్ & డిజిటల్ స్కామ్‌ల నుండి రక్షణ",
        "paste_prompt": "సందేహాస్పద సందేశం, SMS లేదా WhatsApp వచనం ఇక్కడ పేస్ట్ చేయండి:",
        "scan_button": "🔍 స్కామ్ కోసం స్కాన్ చేయండి",
        "analysis_result": "విశ్లేషణ ఫలితం",
        "emergency_action": "🚨 అత్యవసర చర్య",
        "call_1930": "1930 హెల్ప్‌లైన్‌కు కాల్ చేయండి",
        "report_cyber": "Cybercrime.gov.inకి రిపోర్ట్ చేయండి",
        "report_chakshu": "Chakshuకు రిపోర్ట్ చేయండి (Sanchar Saathi)",
        "chakshu_cta": "నకిలీ KYC / SIM / SMS స్కామ్‌లను Sanchar Saathiలో రిపోర్ట్ చేయండి",
        "analyzing": "డిజిటల్ ధర్మాతో విశ్లేషిస్తోంది...",
        "please_paste": "దయచేసి ముందుగా ఒక సందేశాన్ని పేస్ట్ చేయండి!",
        "upload_key": "మీ User Gemini API Key అందించండి (సెషన్ మాత్రమే)",
        "use_secrets": "Streamlit Secrets నుండి యాప్-స్థాయి కీ ని ఉపయోగించండి",
        "quantum_title": "క్వాంటమ్ 'డిజిటల్ ధర్మ' అనుకరణ",
        "quantum_explain": "సూపర్‌పోజిషన్ చూపుతోంది; అఖిక ఫలితం AI నమ్మకంగా మరియు క్వాంటమ్ ఫలితాన్ని కలపడం.",
        "raw_response": "రా మోడల్ స్పందన (డీబగ్గింగ్)"
    }
}

# -----------------------
# SESSION STATE INIT
# -----------------------
def init_session():
    defaults = {
        "language": "English",
        "last_input": "",
        "last_parsed": None,
        "last_score": None,
        "user_api_key": None,
        "logged_in_user": None,  # populate after OAuth
        "quantum_state": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# -----------------------
# AUTHENTICATION / USER LOGIN (placeholder)
# -----------------------
def google_oauth_placeholder():
    """
    Placeholder for Google OAuth integration.
    Streamlit does not provide st.login() natively. For production, integrate:
      - Authlib + Google OAuth2
      - Or setup Identity Platform + reverse-proxy + secure JWT verification.
    This function provides a simple simulated login UX to toggle "logged_in_user" session state.
    """
    col1, col2 = st.sidebar.columns([3,1])
    if st.session_state.get("logged_in_user"):
        col1.markdown(f"**User:** {st.session_state['logged_in_user']}")
        if col2.button(MULTI[st.session_state["language"]]["logout"]):
            st.session_state["logged_in_user"] = None
            st.success("Signed out")
    else:
        if col1.button(MULTI[st.session_state["language"]]["login"]):
            # Simulate sign-in (replace with real OAuth in production)
            st.session_state["logged_in_user"] = "user@example.com"
            st.success("Signed in as user@example.com")
            # NOTE: After real OAuth, you SHOULD NOT store sensitive tokens in client-side session_state unencrypted.

# -----------------------
# API KEY HANDLING (per-session)
# -----------------------
def get_effective_api_key():
    """
    Priority:
      1) per-session user provided key (st.session_state['user_api_key'])
      2) app-level key from st.secrets['GOOGLE_API_KEY']
      3) None -> error
    The user-provided key is stored only in session_state and is lost when session ends.
    """
    if st.session_state.get("user_api_key"):
        return st.session_state["user_api_key"]
    return st.secrets.get("GOOGLE_API_KEY") if "GOOGLE_API_KEY" in st.secrets else None

def user_key_input_ui(labels):
    """
    Sidebar control to allow a logged-in user to enter their own Gemini API key for the session.
    If the user enters a key, it is stored only in st.session_state['user_api_key'].
    Provide an option to use the app-level secret instead.
    """
    st.sidebar.write("---")
    st.sidebar.markdown("### API Key (session)")
    if st.session_state.get("logged_in_user"):
        key = st.sidebar.text_input(labels["upload_key"], type="password", value=st.session_state.get("user_api_key") or "")
        if key:
            st.session_state["user_api_key"] = key.strip()
            st.sidebar.success("User key stored for this session only.")
        use_app = st.sidebar.checkbox(labels["use_secrets"], value=not bool(st.session_state.get("user_api_key")))
        if use_app:
            st.session_state["user_api_key"] = None
    else:
        st.sidebar.info("Sign in to provide a per-session API key.")

# -----------------------
# AI CONFIGURATION + ERROR HANDLING
# -----------------------
def configure_model_with_key(api_key: Optional[str]):
    """
    Configure google.generativeai with the provided api_key.
    Wrap in try/except to avoid raising on configuration failure.
    Returns a model object or None.
    """
    if not api_key:
        st.error("No API key available. Add GOOGLE_API_KEY to Streamlit Secrets or provide a per-session key.")
        return None
    try:
        genai.configure(api_key=api_key)
        # choose model family; allow fallback later if unavailable
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        st.error(f"Failed to configure GenAI client: {e}")
        return None

# -----------------------
# PROMPT BUILDING (Advanced Forensic Investigator)
# -----------------------
def build_forensic_prompt(message: str, language: str) -> str:
    """
    Build an advanced prompt instructing the model to act as a Digital Forensic Investigator.
    The model must return strict JSON only to ease parsing.
    JSON schema requested:
    {
      "is_scam":"yes|no|suspect",
      "score": int (0-100),
      "explanations": {"en":"", "hi": "", "bn":"", ...},
      "social_engineering_tactics": ["pretexting", "authority", ...],
      "matched_patterns": ["KYC expiry", ...]
    }
    """
    patterns = [
        "electricity bill disconnected",
        "KYC expiry",
        "WhatsApp job offer",
        "bank OTP request",
        "refund/payment due",
        "lottery/prize",
        "fake URL / short link",
        "request to install app or share KYC",
        "UPI/phone transfer request"
    ]
    pattern_text = "; ".join(patterns)
    instruct = (
        f"You are a Digital Forensic Investigator specialized in Indian scam patterns. "
        f"Analyze the message and return ONLY a JSON object matching the schema described below. "
        f"Look explicitly for patterns: {pattern_text}. Provide social engineering tactics (e.g., authority, urgency, scarcity, pretexting, baiting). "
        f"Provide concise explanations in multiple languages if possible. Provide an integer 'score' between 0 and 100 where 100 is certainly a scam.\n\n"
        f"Message: \"\"\"{message}\"\"\"\n\n"
        f"Return JSON only. Ensure the score is an integer."
    )
    return instruct

# -----------------------
# MODEL CALL + PARSING
# -----------------------
def call_model_and_parse(model, prompt: str) -> Dict[str, Any]:
    """
    Safe wrapper to call model.generate_content and parse a JSON response.
    If the model fails or returns non-JSON, fallback to best-effort parsing.
    """
    raw = ""
    try:
        response = model.generate_content(prompt)
        # Extract text safely
        if hasattr(response, "text") and response.text:
            raw = response.text
        elif hasattr(response, "candidates") and response.candidates:
            raw = getattr(response.candidates[0], "content", getattr(response.candidates[0], "text", str(response.candidates[0])))
        else:
            raw = str(response)
    except Exception as e:
        raw = json.dumps({"error": str(e)})
        st.error("Failed to call the model. Using conservative suspect fallback.")
    parsed = parse_model_response(raw)
    parsed["raw"] = raw
    return parsed

def parse_model_response(text: str) -> Dict[str, Any]:
    """
    Attempt strict JSON load; fall back to regex extraction.
    Expected fields: is_scam, score, explanations (dict), social_engineering_tactics (list), matched_patterns (list)
    Returns a dict with normalized fields and safe defaults.
    """
    try:
        data = json.loads(text)
        # normalize
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
            "raw": text
        }
    except Exception:
        # fallback heuristics
        score_match = re.search(r"(\b[0-9]{1,3}\b)\s*(%|percent)?", text)
        score = 50
        if score_match:
            try:
                c = int(score_match.group(1))
                if 0 <= c <= 100:
                    score = c
            except:
                pass
        is_scam = "suspect"
        if re.search(r"\b(scam|fraud|fake|malicious)\b", text, re.I):
            is_scam = "yes"
        elif re.search(r"\b(not a scam|safe|benign)\b", text, re.I):
            is_scam = "no"
        known_patterns = ["electricity", "bill", "KYC", "job", "WhatsApp", "OTP", "link", "refund", "lottery", "prize", "UPI"]
        matched = [p for p in known_patterns if re.search(p, text, re.I)]
        return {
            "is_scam": is_scam,
            "score": score,
            "explanations": {"en": text},
            "tactics": [],
            "matched_patterns": matched,
            "raw": text
        }

# -----------------------
# RISK METER UTILITIES
# -----------------------
def risk_label_and_color(score: int):
    """
    Map score-> label & color. Keep consistent and documented here.
    0-33: Safe (Green)
    34-66: Suspect (Yellow)
    67-100: Scam (Red)
    """
    if score <= 33:
        return "Safe", "#2ecc71"
    elif score <= 66:
        return "Suspect", "#f1c40f"
    else:
        return "Scam", "#e74c3c"

# -----------------------
# QUANTUM 'DIGITAL DHARMA' SIMULATION
# -----------------------
def hadamard():
    """2x2 Hadamard gate"""
    return (1 / math.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)

def quantum_superposition_and_measure(model_score: int, seed: Optional[int] = None):
    """
    Create a biased qubit state based on the model_score, apply Hadamard to show superposition, then measure.
    model_score: 0..100 (higher => more likely 'scam')
    Steps:
      - map model_score to initial amplitude for |1> vs |0> as sqrt(p)
      - apply H
      - compute probabilities, sample measurement (collapse)
    Returns dict with amplitudes, probabilities, measured_state (0 safe, 1 scam)
    """
    # map score -> probability of |1> (scam) initially
    p1 = np.clip(model_score / 100.0, 0.0, 1.0)
    # amplitude vector (|0>, |1>) using square roots
    a0 = math.sqrt(max(0.0, 1 - p1))
    a1 = math.sqrt(max(0.0, p1))
    state = np.array([[a0], [a1]], dtype=complex)
    H = hadamard()
    superposed = H @ state
    probs = np.abs(superposed) ** 2
    # Normalize probability just to be safe
    probs = probs / np.sum(probs)
    rng = np.random.default_rng(seed)
    measured = rng.choice([0, 1], p=[float(probs[0]), float(probs[1])])
    result = {
        "initial_amplitudes": [float(np.round(a0.real, 4)), float(np.round(a1.real, 4))],
        "superposed_amplitudes": [float(np.round(superposed[0].real, 4)), float(np.round(superposed[1].real, 4))],
        "probabilities": [float(np.round(probs[0], 4)), float(np.round(probs[1], 4))],
        "measured": measured  # 0 -> safe, 1 -> scam
    }
    return result

# -----------------------
# RENDERING / UI
# -----------------------
def render_main_ui():
    labels = MULTI[st.session_state["language"]]
    # Title card
    st.markdown(f"<div class='glass'><h1 style='margin-bottom:6px'>{labels['title']}</h1><p style='margin-top:0;color:#cfe9ff'>{labels['subtitle']}</p></div>", unsafe_allow_html=True)
    st.write("")

    # Two-column main area
    left, right = st.columns([2, 1])

    with left:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        user_input = st.text_area(labels["paste_prompt"], value=st.session_state.get("last_input", ""), height=180)
        st.session_state["last_input"] = user_input
        st.markdown("</div>", unsafe_allow_html=True)

        # Scan button
        if st.button(labels["scan_button"], key="scan", help="Launch forensic analysis", ):
            if not user_input:
                st.warning(labels["please_paste"])
            else:
                # Determine API key and configure model
                api_key = get_effective_api_key()
                model = configure_model_with_key(api_key)
                if model:
                    with st.spinner(labels["analyzing"]):
                        prompt = build_forensic_prompt(user_input, st.session_state["language"])
                        parsed = call_model_and_parse(model, prompt)
                        st.session_state["last_parsed"] = parsed
                        st.session_state["last_score"] = parsed.get("score", 50)
                        # Quantum simulation using model score
                        qres = quantum_superposition_and_measure(st.session_state["last_score"])
                        st.session_state["quantum_state"] = qres

                        render_analysis(parsed, qres)
                else:
                    st.error("AI model unavailable. Check API key and network.")

        # If we have previous result and no new scan triggered, show persisted
        if st.session_state.get("last_parsed") and not st.session_state.get("quantum_state"):
            # Show previous analysis (no quantum collapse saved)
            prev = st.session_state["last_parsed"]
            qprev = quantum_superposition_and_measure(prev.get("score", 50))
            st.session_state["quantum_state"] = qprev
            render_analysis(prev, qprev)

        elif st.session_state.get("last_parsed") and st.session_state.get("quantum_state"):
            # Show last saved analysis (consistent across language switches)
            render_analysis(st.session_state["last_parsed"], st.session_state["quantum_state"])

    with right:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### Session & Keys")
        # Fake OAuth / login UX
        google_oauth_placeholder()
        user_key_input_ui(labels)
        st.markdown("</div>", unsafe_allow_html=True)

        # Emergency & Chakshu Card
        st.markdown("<div class='glass' style='margin-top:14px'>", unsafe_allow_html=True)
        st.markdown(f"### {labels['emergency_action']}")
        if st.button(labels["call_1930"], key="call1930"):
            st.write("📞 Dialing 1930...")
            st.markdown("[Click here to call 1930](tel:1930)")
        if st.button(labels["report_cyber"], key="reportcyber"):
            st.write("Redirecting to official portal...")
            st.markdown("[Visit Portal](https://cybercrime.gov.in)")
        st.markdown("---")
        st.markdown(f"### {labels['report_chakshu']}")
        st.markdown(labels["chakshu_cta"])
        st.markdown("[Report on Sanchar Saathi (DoT)](https://sancharsaathi.gov.in)")
        st.markdown("</div>", unsafe_allow_html=True)

def render_analysis(parsed: Dict[str, Any], qres: Dict[str, Any]):
    labels = MULTI[st.session_state["language"]]
    st.markdown("<div class='glass' style='margin-top:16px'>", unsafe_allow_html=True)
    st.markdown(f"## {labels['analysis_result']}")

    score = int(parsed.get("score", 50))
    label, color = risk_label_and_color(score)

    # Progress bar (0-100)
    st.progress(score / 100)

    # Colored badge
    st.markdown(f"<div style='background:{color};padding:10px;border-radius:8px;color:#001010;font-weight:700;text-align:center'>{label} — Risk Score: {score}%</div>", unsafe_allow_html=True)

    # Quantum superposition visualization (textual)
    st.markdown(f"### {MULTI[st.session_state['language']]['quantum_title']}")
    st.markdown(MULTI[st.session_state['language']]['quantum_explain'])
    st.write("Initial amplitudes (|0>, |1>):", qres["initial_amplitudes"])
    st.write("After Hadamard - superposed amplitudes:", qres["superposed_amplitudes"])
    st.write("Probabilities (|0>, |1>):", qres["probabilities"])
    st.write("Quantum collapse result:", "SCAM" if qres["measured"] == 1 else "SAFE")

    # Matched patterns and tactics
    st.markdown("**Matched patterns:** " + (", ".join(parsed.get("matched_patterns", []) or ["None"]) ))
    st.markdown("**Social Engineering Tactics detected:** " + (", ".join(parsed.get("tactics", []) or ["None"]) ))

    # Explanations (multilingual fallback)
    exps = parsed.get("explanations", {})
    # Try language-specific explanation
    lang = st.session_state["language"]
    if exps.get(lang[:2].lower()) or exps.get("en"):
        st.markdown("**Explanation:**")
        st.write(exps.get(lang[:2].lower(), exps.get("en", parsed.get("raw"))))
    else:
        st.write(exps or parsed.get("raw"))

    # Raw for transparency
    with st.expander(MULTI[st.session_state["language"]]["raw_response"]):
        st.code(parsed.get("raw", ""))

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# LANGUAGE TOGGLE (instant update)
# -----------------------
def language_ui():
    lang = st.sidebar.selectbox("Language / भाषा", list(MULTI.keys()), index=list(MULTI.keys()).index(st.session_state["language"]))
    st.session_state["language"] = lang

# -----------------------
# ENTRYPOINT
# -----------------------
def main():
    language_ui()
    render_main_ui()

if __name__ == "__main__":
    main()
