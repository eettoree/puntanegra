import streamlit as st
import json
import time
from groq import Groq

# --- CONFIGURAZIONE HOTEL PUNTA NEGRA ---
try:
    GROQ_KEY = st.secrets["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"]
except:
    GROQ_KEY = "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"

WHATSAPP_NUMBER = "39079930222" # Numero Hotel Punta Negra
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
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_hotel_db():
    try:
        with open('immobili.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def get_hotel_recommendations(query):
    db = load_hotel_db()
    matches = []
    q = query.lower()
    for p in db:
        if any(word in q for word in p['t'].lower().split()) or any(word in q for word in p['desc'].lower().split()):
            matches.append(p)
    return matches[:3]

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
        return "Spiacente, il servizio concierge è momentaneamente offline. Chiami lo +39 079 930222."

# --- APP EXECUTION ---
apply_hotel_ui()

if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome = "Benvenuto all'**Hotel Punta Negra Alghero**. Sono il suo Concierge Digitale. Come posso aiutarla a pianificare il suo soggiorno?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Vorrei una camera vista mare..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown('<div class="skeleton"></div><div class="skeleton" style="width:70%"></div>', unsafe_allow_html=True)
        
        response = call_concierge_ai(st.session_state.messages)
        placeholder.empty()

        # Typing Effect
        full_text = ""
        type_area = st.empty()
        for word in response.split():
            full_text += word + " "
            type_area.markdown(full_text + "▌")
            time.sleep(0.03)
        type_area.markdown(response)

        # Recommendation Cards
        matches = get_hotel_recommendations(prompt)
        if matches:
            st.markdown("### 🛏️ Soluzioni consigliate")
            cols = st.columns(len(matches))
            for i, p in enumerate(matches):
                with cols[i]:
                    wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text=Vorrei%20informazioni%20per%20la%20camera:%20{p['t'].replace(' ', '%20')}"
                    st.markdown(f"""
                        <div class="hotel-card">
                            <img src="{p['img']}" class="card-img">
                            <div class="card-body">
                                <div class="card-title">{p['t']}</div>
                                <div style="font-size:12px; color:#ccc; height:40px; overflow:hidden;">{p['desc']}</div>
                                <div class="btn-grid">
                                    <a href="{p['u']}" target="_blank" class="btn-web">DETTAGLI</a>
                                    <a href="{wa_url}" target="_blank" class="btn-wa">PRENOTA</a>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})