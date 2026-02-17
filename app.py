import streamlit as st
import json
import time
import urllib.parse
from groq import Groq

# --- CONFIGURAZIONE HOTEL PUNTA NEGRA ---
if "GROQ_API_KEY" in st.secrets:
    GROQ_KEY = st.secrets["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"]
else:
    GROQ_KEY = "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"

WHATSAPP_NUMBER = "39079930222"
# Link ufficiale Vertical Booking
BOOKING_URL = "https://reservations.verticalbooking.com/premium/index.html?id_albergo=71&dc=661&lingua_int=ita&id_stile=17978"

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
        
        /* Chat Container & Bubbles */
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

        /* Hotel Property Cards */
        .hotel-card {{
            background: #0D2137; 
            border: 1px solid rgba(26, 75, 132, 0.3);
            border-radius: 18px; 
            overflow: hidden; 
            margin-bottom: 25px;
            transition: transform 0.3s ease;
        }}
        .hotel-card:hover {{ transform: translateY(-5px); border-color: {H_BLUE}; }}
        .card-img {{ width: 100%; height: 210px; object-fit: cover; }}
        .card-body {{ padding: 22px; }}
        .card-title {{ font-family: 'Playfair Display', serif; font-size: 19px; color: white; margin-bottom: 8px; }}
        .card-desc {{ font-size: 13px; color: #ccc; margin-bottom: 15px; height: 40px; overflow: hidden; }}
        
        /* Button Grid */
        .btn-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }}
        .btn-web {{ text-align: center; background: transparent; border: 1px solid {H_BLUE}; color: white !important; text-decoration: none; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: 500; }}
        .btn-wa {{ text-align: center; background: #25D366; color: white !important; text-decoration: none; padding: 10px; border-radius: 8px; font-size: 12px; font-weight: bold; }}
        .btn-booking {{ display: block; text-align: center; background: {H_BLUE}; color: white !important; text-decoration: none; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: bold; margin-top: 10px; }}
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_hotel_db():
    try:
        # Carica il file immobili.json con i dati dell'hotel
        with open('immobili.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def get_hotel_recommendations(query, response_text):
    db = load_hotel_db()
    if not db: return []
    
    matches = []
    # Analisi sia dell'input utente che della risposta dell'AI per trovare match
    q = (query + " " + response_text).lower()
    
    for p in db:
        # Match per titolo o categoria (Camere/Eventi)
        if p.get('t', '').lower() in q or p.get('tp', '').lower() in q:
            matches.append(p)
        # Match per parole chiave (es. "vista mare", "suite")
        elif any(word in q for word in p.get('t', '').lower().split()):
            matches.append(p)
            
    # Ritorna i primi 3 risultati unici
    unique_matches = {v['u']: v for v in matches}.values()
    return list(unique_matches)[:3]

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
        return f"Spiacente, il servizio concierge è momentaneamente non disponibile. (Dettaglio: {str(e)})"

# --- EXECUTION ---
apply_hotel_ui()

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = (
        "Benvenuto all'**Hotel Punta Negra**. Sono il suo Concierge Digitale. "
        "Desidera informazioni su un soggiorno, sulla disponibilità delle camere o sta pianificando un evento?\n\n"
        "*Welcome! I am your Digital Concierge. How can I assist you today?*"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome})

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Scriva qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = call_concierge_ai(st.session_state.messages)
        st.markdown(response)

        # Logica Cards
        matches = get_hotel_recommendations(prompt, response)
        if matches:
            st.markdown("### 💎 Soluzioni suggerite")
            cols = st.columns(len(matches))
            for i, p in enumerate(matches):
                with cols[i]:
                    # Messaggio dinamico per WhatsApp
                    wa_msg = f"Buongiorno, vorrei informazioni per: {p['t']}"
                    wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(wa_msg)}"
                    
                    # Differenziazione bottoni tra Soggiorno ed Eventi
                    is_event = p.get('tp') == "Eventi"
                    btn_wa_label = "PREVENTIVO" if is_event else "WHATSAPP"
                    
                    st.markdown(f"""
                        <div class="hotel-card">
                            <img src="{p.get('img', '')}" class="card-img">
                            <div class="card-body">
                                <div class="card-title">{p.get('t', '')}</div>
                                <div class="card-desc">{p.get('desc', '')[:80]}...</div>
                                <div class="btn-grid">
                                    <a href="{p.get('u', '#')}" target="_blank" class="btn-web">INFO</a>
                                    <a href="{wa_url}" target="_blank" class="btn-wa">{btn_wa_label}</a>
                                </div>
                                {"" if is_event else f"<a href='{BOOKING_URL}' target='_blank' class='btn-booking'>PRENOTA ORA</a>"}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})
