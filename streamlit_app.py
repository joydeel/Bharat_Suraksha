import json
import re
from typing import Dict, Any, List, Optional

import streamlit as st
import google.generativeai as genai

# =========================
# PAGE CONFIGURATION
# =========================
st.set_page_config(page_title="Bharat Suraksha AI", page_icon="🛡️")

# =========================
# TIRANGA THEME CSS (Saffron, White, Green)
# =========================
st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS & DIGITAL DHARMA LOGIC (MODULAR)
# =========================


def configure_ai() -> Optional[Any]:
    """
    Configure the Google GenAI client using Streamlit secrets.
    Returns a configured model object or None on failure.

    Digital Dharma note:
    - The GenAI model is used as a judgment engine to identify intent ("Dharma")
      in incoming messages. The model is prompted to look for Indian fraud
      patterns (e.g., "electricity bill disconnected", "KYC expiry", "WhatsApp job offers")
      and to output a compact, machine-parsable response that includes a risk score
      (0-100) and explanations in both English and Hindi.

    Security note:
    - Keep keys in Streamlit Secrets or environment variables. Do not print keys.
    """
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception:
        st.error("API Key not found or GenAI configuration failed. Please add GOOGLE_API_KEY to Streamlit Secrets.")
        return None


def init_session_state() -> None:
    """
    Initialize session_state keys so results persist across reruns and language switches.
    We store:
      - language: 'English' or 'Hindi'
      - last_input: the last scanned message
      - last_response: the raw model response text (for debugging/view)
      - last_score: numeric risk score 0-100
      - last_parsed: structured parsed result (dict)
    """
    state_defaults = {
        "language": "English",
        "last_input": "",
        "last_response": None,
        "last_score": None,
        "last_parsed": None,
    }
    for key, default in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def build_translations() -> Dict[str, Dict[str, str]]:
    """
    Returns a translation map for UI labels. Add more labels as needed.
    """
    return {
        "English": {
            "title": "🛡️ Bharat Suraksha AI",
            "subtitle": "*Protecting India from Digital Scams*",
            "paste_prompt": "Paste the suspicious message, SMS, or WhatsApp text here:",
            "scan_button": "🔍 SCAN FOR SCAMS",
            "analysis_result": "Analysis Result",
            "emergency_action": "🚨 Emergency Action",
            "call_1930": "Call 1930 Helpline",
            "report_cyber": "Report to Cybercrime.gov.in",
            "report_chakshu": "Report to Chakshu (DoT / Sanchar Saathi)",
            "chakshu_cta": "Report forged KYC / SMS scams to Sanchar Saathi",
            "analyzing": "Analyzing with Digital Dharma...",
            "please_paste": "Please paste a message first!",
        },
        "Hindi": {
            "title": "🛡️ भारत सुरक्षा AI",
            "subtitle": "*डिजिटल स्कैम से भारत की सुरक्षा*",
            "paste_prompt": "संदेहास्पद संदेश, SMS या WhatsApp टेक्स्ट यहाँ पेस्ट करें:",
            "scan_button": "🔍 स्कैम के लिए स्कैन करें",
            "analysis_result": "विश्लेषण परिणाम",
            "emergency_action": "🚨 आपातकालीन कार्रवाई",
            "call_1930": "1930 हेल्पलाइन कॉल करें",
            "report_cyber": "Cybercrime.gov.in पर रिपोर्ट करें",
            "report_chakshu": "Chakshu को रिपोर्ट करें (DoT / Sanchar Saathi)",
            "chakshu_cta": "नकली KYC / SMS स्कैम Sanchar Saathi पर रिपोर्ट करें",
            "analyzing": "डिजिटल धर्मा के साथ विश्लेषण कर रहे हैं...",
            "please_paste": "कृपया पहले एक संदेश पेस्ट करें!",
        },
    }


def build_sidebar(translations: Dict[str, Dict[str, str]]) -> None:
    """
    Sidebar UI: language toggle and menu information.
    """
    st.sidebar.image("https://img.icons8.com/color/96/shield-with-crown.png")
    st.sidebar.title("App Menu")

    # Language toggle
    language = st.sidebar.selectbox(
        "Language / भाषा", ["English", "Hindi"], index=0 if st.session_state["language"] == "English" else 1
    )
    # Persist language selection in session_state without clearing previous results.
    st.session_state["language"] = language

    st.sidebar.info("This AI analyzes the 'Dharma' (intent) of messages to detect fraud.")
    st.sidebar.write("---")
    st.sidebar.write("🇮🇳 **Digital India Initiative 2026**")


def craft_prompt(message: str, language: str) -> str:
    """
    Build a vernacular-aware prompt for the Gemini model.
    The prompt requests a JSON response to make parsing deterministic.

    Requested JSON format (strict):
    {
      "is_scam": "yes" | "no" | "suspect",
      "score": <int 0-100>,
      "explanation_en": "<english explanation>",
      "explanation_hi": "<hindi explanation>",
      "matched_patterns": ["pattern1", "pattern2", ...]
    }

    Digital Dharma scoring heuristics (described to model):
      - Look for Indian scam tropes: electricity bill disconnect, fake KYC expiry, WhatsApp job offers,
        fake bank OTP, refund offers, lottery/prize, urgent money/fraudulent links, numbers/UPIs.
      - Increase score when multiple strong indicators present (financial ask, urgency, spoofed URL/phone).
      - Lower score if message is informational or from known official channels.
    """
    patterns = [
        "electricity bill disconnected",
        "KYC expiry",
        "WhatsApp job offer",
        "bank OTP / password request",
        "refund / payment due",
        "prize / lottery",
        "link to click / short URL",
        "ask to install app or share KYC",
        "UPI/phone number for transfer",
    ]
    pattern_text = "; ".join(patterns)

    instruction_language = "English"
    if language == "Hindi":
        instruction_language = "Hindi"

    prompt = f"""
You are a fraud detection assistant tuned for Indian scams called 'Digital Dharma'. Analyze the following message and return a strict JSON object only (no extra commentary).
Language preference: {language}
Message: \"\"\"{message}\"\"\"

Tasks:
- Identify if this is likely a scam. Reply with "yes", "no", or "suspect" in the "is_scam" field.
- Produce a numeric risk "score" between 0 and 100 where higher means more likely a scam.
- Provide brief explanations in both English and Hindi using fields "explanation_en" and "explanation_hi".
- List any matched patterns from this list (or others you detect): {pattern_text} in an array "matched_patterns".
- If uncertain, use "suspect" and give the reason.

Digital Dharma scoring guidance (be explicit in your reasoning):
- Presence of urgent financial request, spoofed links, or OTP/KYC requests => raise score.
- Generic or benign notification from a verified service => lower score.
- Multiple fraud indicators (2+) => +30 points, single indicator => +15 points.
- If you cannot safely determine, set "score" to a conservative mid-value and flag "suspect".

Return only valid JSON. Ensure the "score" is an integer 0-100.
"""
    return prompt


def parse_model_response(text: str) -> Dict[str, Any]:
    """
    Attempt to parse JSON returned by the model. If the model returned explanatory text,
    try to extract a numeric score using regex and build a best-effort result.

    Returns a dict:
      - is_scam: "yes"/"no"/"suspect"
      - score: int
      - explanation_en: str
      - explanation_hi: str
      - matched_patterns: list
    """
    # Try direct JSON parse
    try:
        data = json.loads(text)
        # sanitize fields
        result = {
            "is_scam": data.get("is_scam", "suspect"),
            "score": int(data.get("score", 50)),
            "explanation_en": data.get("explanation_en", "") or "",
            "explanation_hi": data.get("explanation_hi", "") or "",
            "matched_patterns": data.get("matched_patterns", []) or [],
            "raw": text,
        }
        return result
    except Exception:
        # Fallback: regex based extraction
        score_match = re.search(r"(\b[0-9]{1,3}\b)\s*(%|percent)?", text)
        score = 50
        if score_match:
            try:
                score_candidate = int(score_match.group(1))
                if 0 <= score_candidate <= 100:
                    score = score_candidate
            except Exception:
                pass

        is_scam = "suspect"
        if re.search(r"\b(yes|scam|fraud|fake|malicious)\b", text, re.I):
            is_scam = "yes"
        elif re.search(r"\b(no|not a scam|benign|safe)\b", text, re.I):
            is_scam = "no"

        # naive matched patterns detection
        known_patterns = [
            "electricity", "bill", "KYC", "job offer", "WhatsApp", "OTP", "link", "refund", "lottery", "prize", "UPI"
        ]
        matched = [p for p in known_patterns if re.search(p, text, re.I)]

        return {
            "is_scam": is_scam,
            "score": int(score),
            "explanation_en": text,
            "explanation_hi": "",
            "matched_patterns": matched,
            "raw": text,
        }


def risk_color_and_label(score: int) -> (str, str):
    """
    Map score to a color and label.
    - 0-33: Safe (Green)
    - 34-66: Suspect (Yellow)
    - 67-100: Scam (Red)
    """
    if score <= 33:
        return "#2ecc71", "Safe"
    if score <= 66:
        return "#f1c40f", "Suspect"
    return "#e74c3c", "Scam"


def analyze_message(model: Any, message: str, language: str) -> Dict[str, Any]:
    """
    Orchestrate the prompt -> model -> parse flow.
    Stores the raw model response and parsed result in session_state.
    """
    prompt = craft_prompt(message, language)

    # Call the model; keep temperature low for deterministic answers
    try:
        # Use the existing generate_content call pattern; adapt if API differs
        response = model.generate_content(prompt)
        # model.generate_content often returns an object; try to extract text
        raw_text = ""
        if hasattr(response, "text") and response.text:
            raw_text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            # some clients return candidates list with 'content' or 'text'
            first = response.candidates[0]
            raw_text = getattr(first, "content", getattr(first, "text", str(first)))
        else:
            raw_text = str(response)
    except Exception as e:
        # If model call fails, store the exception and return a conservative suspect result
        raw_text = f'{{"error":"{str(e)}"}}'
        st.error("Model call failed. See raw response in details.")

    parsed = parse_model_response(raw_text)

    # Persist results in session state
    st.session_state["last_input"] = message
    st.session_state["last_response"] = raw_text
    st.session_state["last_score"] = parsed.get("score", 50)
    st.session_state["last_parsed"] = parsed

    return parsed


def render_results(parsed: Dict[str, Any], language: str, translations: Dict[str, Dict[str, str]]) -> None:
    """
    Display parsed analysis results with a progress bar and a colored badge/metric.
    Keeps explanations in English and Hindi (as available).
    """
    labels = translations[language]

    st.subheader(labels["analysis_result"])

    score = int(parsed.get("score", 50))
    is_scam = parsed.get("is_scam", "suspect")
    explanation_en = parsed.get("explanation_en", "")
    explanation_hi = parsed.get("explanation_hi", "")
    matched = parsed.get("matched_patterns", [])

    # Visual risk meter
    st.progress(score / 100)

    color, label = risk_color_and_label(score)
    badge_html = f"""
    <div style="background:{color};padding:12px;border-radius:8px;color:#fff;text-align:center;font-weight:700">
      {label} — Risk Score: {score}%
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

    # Matched patterns
    if matched:
        st.markdown(f"**Matched patterns:** {', '.join(matched)}")
    else:
        st.markdown("**Matched patterns:** None detected")

    # Explanations in selected language first, then alternate
    if language == "Hindi":
        if explanation_hi:
            st.markdown(f"**व्याख्या (हिंदी):** {explanation_hi}")
        if explanation_en:
            st.markdown(f"**Explanation (English):** {explanation_en}")
    else:
        if explanation_en:
            st.markdown(f"**Explanation (English):** {explanation_en}")
        if explanation_hi:
            st.markdown(f"**व्याख्या (हिंदी):** {explanation_hi}")

    # Show raw response for transparency (collapsible)
    with st.expander("Raw model response (for debugging)"):
        st.code(parsed.get("raw", ""))


def build_emergency_and_chakshu_section(translations: Dict[str, Dict[str, str]]) -> None:
    """
    Build the emergency action area including Chakshu (Sanchar Saathi) integration.
    """
    labels = translations[st.session_state["language"]]
    st.markdown("---")
    st.subheader(labels["emergency_action"])
    col1, col2 = st.columns(2)

    with col1:
        if st.button(labels["call_1930"]):
            st.write("📞 Dialing 1930...")
            st.markdown("[Click here to call 1930](tel:1930)")

    with col2:
        if st.button(labels["report_cyber"]):
            st.write("Redirecting to official portal...")
            st.markdown("[Visit Portal](https://cybercrime.gov.in)")

    # Chakshu integration (DoT Sanchar Saathi) — dedicated section
    st.write("---")
    st.subheader(labels["report_chakshu"])
    st.markdown(labels["chakshu_cta"])
    st.markdown(
        "[Report on Sanchar Saathi (DoT)](https://sancharsaathi.gov.in)  \n"
        "Sanchar Saathi (DoT) provides reporting for forged KYC, SIM swapping, and SMS scams."
    )


# =========================
# MAIN APP
# =========================
def main():
    init_session_state()
    model = configure_ai()
    translations = build_translations()

    # UI Titles
    st.title(translations[st.session_state["language"]]["title"])
    st.write(f"### {translations[st.session_state['language']]['subtitle']}")

    # Sidebar with language and info (this will update st.session_state['language'])
    build_sidebar(translations)

    # Input area (use session_state to repopulate last input if present)
    labels = translations[st.session_state["language"]]
    default_text = st.session_state["last_input"] or ""
    user_input = st.text_area(labels["paste_prompt"], value=default_text, height=150)

    # Store typed input in session state but do not clear previous results until scan
    st.session_state["current_input"] = user_input

    # Scan button
    if st.button(labels["scan_button"]):
        if user_input and model:
            with st.spinner(labels["analyzing"]):
                parsed = analyze_message(model, user_input, st.session_state["language"])
                render_results(parsed, st.session_state["language"], translations)
        elif not user_input:
            st.warning(labels["please_paste"])
        else:
            st.error("AI model is not configured. Cannot analyze message.")

    # If there are previous results, show them (this keeps results visible after language toggle)
    elif st.session_state.get("last_parsed"):
        st.info("Showing last analysis (persistent across language switching).")
        render_results(st.session_state["last_parsed"], st.session_state["language"], translations)

    # Emergency and Chakshu section
    build_emergency_and_chakshu_section(translations)


if __name__ == "__main__":
    main()
