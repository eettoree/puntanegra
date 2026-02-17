import streamlit as st
import json
import time
from groq import Groq

# --- CONFIGURAZIONE HOTEL PUNTA NEGRA ---
# Gestione sicura della chiave API per Streamlit Cloud
if "GROQ_API_KEY" in st.secrets:
    GROQ_KEY = st.secrets["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"]
else:
    GROQ_KEY = "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"

WHATSAPP_NUMBER = "39079930222"
# Link corretto Vertical Booking
BOOKING_URL = "https://reservations.verticalbooking.com/premium/index.html?id_albergo=71&dc=661&lingua_int=ita&id_stile=17978&_ga=2.13048119.1438568113.1771324260-655987707.1771324259"

H_BLUE = "#1A4B84"
H_SAND = "#F4F1EA"
H_DARK = "#0A192F"

st.set_page_config(page_title="Punta Negra Concierge AI", page_icon="🌊", layout="centered")

# --- UI CUSTOM (OCEAN STYLE) ---
def apply_hotel_ui():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');
        
        .stApp {{ background-color: {H_DARK}; color: {H_SAND}; font-family: 'Inter', sans-serif; }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none; }}
        
        .stChatMessage {{ 
            border-radius: 20px; 
            padding: 20px; 
            margin-bottom: 15px; 
            border: 1px solid rgba(255,255,255,0.1) !important;
            background-color: transparent !important;
        }}
        .stChatMessage[data-testid="stChatMessageAssistant"] {{ 
            background-color: rgba(26, 75, 132, 0.2) !important; 
            border-left: 4px solid {H_BLUE} !important; 
        }}

        .skeleton {{ height: 16px; background: #162A44; border-radius: 8px; margin: 10px 0; animation: shimmer 2s infinite; }}
        @keyframes shimmer {{ 0% {{ opacity: 0.3; }} 50% {{ opacity: 0.6; }} 100% {{ opacity: 0.3; }} }}

        div[data-testid="stChatInput"] {{
            border-radius: 15px !important;
            border: 1px solid {H_BLUE} !important;
            background-color: #0D2137 !important;
        }}

        .hotel-card {{
            background: #0D2137; 
            border: 1px solid rgba(26, 75, 132, 0.3);
            border-radius: 15px; 
            overflow: hidden; 
            margin-bottom: 20px;
        }}
        .card-img {{ width: 100%; height: 200px; object-fit: cover; }}
        .card-body {{ padding: 20px; }}
        .card-title {{ font-family: 'Playfair Display', serif; font-size: 18px; color: white; margin-bottom: 10px; }}
        
        .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }}
        .btn-web {{ text-align: center; background: transparent; border: 1px solid {H_BLUE}; color: white !important; text-decoration: none; padding: 10px; border-radius: 8px; font-size: 12px; }}
        .btn-wa {{ text-align: center; background: #25D366; color: white !important; text-decoration: none; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: bold; }}
        .btn-booking {{ display: block; text-align: center; background: {H_BLUE}; color: white !important; text-decoration: none; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: bold; margin-top: 10px; }}
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_hotel_db():
    try:
        with open('immobili.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def get_hotel_recommendations(query):
    db = load_hotel_db()
    if not db:
        return []
    matches = []
    q = query.lower()
    for p in db:
        # Ricerca per titolo o categoria
        if any(word in q for word in p.get('t', '').lower().split()) or \
           any(word in q for word in p.get('tp', '').lower().split()):
            matches.append(p)
    return matches[:3]

# Inizializzazione Groq
client = Groq(api_key=GROQ_KEY)

def call_concierge_ai(messages):
    try:
        with open("istruzioni.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            temperature=0.1
        )
        return completion.choices[0].message.content
    except Exception as e:
        return "Service temporarily unavailable. Please contact +39 079 930222."

# --- ESECUZIONE APP ---
apply_hotel_ui()

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = (
        "Benvenuto all'**Hotel Punta Negra**. Sono il suo Concierge Digitale. "
        "Desidera informazioni su un soggiorno o sta pianificando un evento?\n\n"
        "*Welcome to **Hotel Punta Negra**. I am your Digital Concierge. "
        "Would you like information about a stay or are you planning an event?*"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# Mostra messaggi precedenti
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Gestione Input
if prompt := st.chat_input("Scriva qui / Write here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown('<div class="skeleton"></div><div class="skeleton" style="width:70%"></div>', unsafe_allow_html=True)
        
        response = call_concierge_ai(st.session_state.messages)
        placeholder.empty()

        # Effetto Scrittura
        full_text = ""
        type_area = st.empty()
        for word in response.split():
            full_text += word + " "
            type_area.markdown(full_text + "▌")
            time.sleep(0.02)
        type_area.markdown(response)

        # Logica Cards
        matches = get_hotel_recommendations(prompt)
        if matches:
            cols = st.columns(len(matches))
            for i, p in enumerate(matches):
                with cols[i]:
                    # Configurazione bottoni in base al tipo (Camere vs Eventi)
                    if p.get('tp') == "Eventi":
                        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text=Preventivo%20evento:%20{p['t'].replace(' ', '%20')}"
                        btn_label = "EVENT INFO"
                        action_btn_html = ""
                    else:
                        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text=Info%20soggiorno%20camera:%20{p['t'].replace(' ', '%20')}"
                        btn_label = "WHATSAPP"
                        action_btn_html = f"<a href='{BOOKING_URL}' target='_blank' class='btn-booking'>BOOK NOW</a>"

                    st.markdown(f"""
                        <div class="hotel-card">
                            <img src="{p.get('img', '')}" class="card-img">
                            <div class="card-body">
                                <div class="card-title">{p.get('t', '')}</div>
                                <div style="font-size:12px; color:#ccc; height:45px; overflow:hidden;">{p.get('desc', '')}</div>
                                <div class="btn-grid">
                                    <a href="{p.get('u', '#')}" target="_blank" class="btn-web">INFO</a>
                                    <a href="{wa_url}" target="_blank" class="btn-wa">{btn_label}</a>
                                </div>
                                {action_btn_html}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})

