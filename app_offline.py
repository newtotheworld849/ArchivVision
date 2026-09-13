import streamlit as st
import sqlite3
import json
import os
from base64 import b64encode
from openai import OpenAI
from dotenv import load_dotenv

# Load API environment variables
load_dotenv()
st.set_page_config(page_title="PartsRecognition", page_icon="📐", layout="wide")

# Minimalist, ETH-inspired CSS styling
st.markdown("""
    <style>
    .reportview-container { background: #ffffff; }
    h1, h2, h3 { font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 300 !important; color: #111111; }
    .stButton>button { background-color: #111111; color: white; border-radius: 0px; border: none; }
    .stButton>button:hover { background-color: #333333; color: white; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATABASE SETUP
# -----------------------------------------------------------------------------
DB_FILE = "archive.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS drawings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            drawing_type TEXT,
            medium TEXT,
            style_era TEXT,
            elements TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(filename, analysis):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO drawings (filename, drawing_type, medium, style_era, elements, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (filename, analysis.get("drawing_type"), analysis.get("medium"), 
          analysis.get("style_era"), ", ".join(analysis.get("detected_elements", [])), 
          analysis.get("architectural_description")))
    conn.commit()
    conn.close()

def fetch_drawings():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM drawings ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# -----------------------------------------------------------------------------
# AI INFERENCE LAYER (Vision API)
# -----------------------------------------------------------------------------
def analyze_drawing_with_ai(image_bytes, filename):
    # BYPASS: Simulating AI responses due to offline testing
    import time
    time.sleep(1) # Simulates network processing lag
    
    # Fake AI responses to populate your database seamlessly
    mock_analysis = {
      "drawing_type": "Assembly Drawing",
      "medium": "Digital CAD Export",
      "style_era": "Modern Compact Grid System",
      "detected_elements": ["Transformer", "Circuit Breaker", "Busbar", "Isolator", "Insulator"],
      "architectural_description": f"A comprehensive visual mapping of substation component layout for {filename}, detailing core terminal spacing."
    }
    return mock_analysis

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ],
            max_tokens=500,
        )
        return json.loads(response.choices.message.content)
    except Exception as e:
        st.error(f"AI Processing Failed: {e}")
        return None

# -----------------------------------------------------------------------------
# APP UI / FRONTEND
# -----------------------------------------------------------------------------
st.title("📐 PartsRecognition")
st.caption("Digital Infrastructure Prototype // Automated Image recognition & Labelling")

# Create a clean side-by-side grid layout
col_upload, col_gallery = st.columns(2, gap="large")

with col_upload:
    st.header("1. Ingest Asset")
    uploaded_file = st.file_uploader("Upload drawing (JPG/PNG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Staged for Archiving", use_container_width=True)
        
        if st.button("Run AI Digitisation & Save", use_container_width=True):
            with st.spinner("Extracting architectural features via VLM..."):
                file_bytes = uploaded_file.read()
                
                # Run AI pipeline
                ai_analysis = analyze_drawing_with_ai(file_bytes, uploaded_file.name)
                
                if ai_analysis:
                    # Save image locally to simulate an archival server storage
                    os.makedirs("archive_vault", exist_ok=True)
                    saved_path = os.path.join("archive_vault", uploaded_file.name)
                    with open(saved_path, "wb") as f:
                        f.write(file_bytes)
                    
                    # Log into SQLite DB
                    save_to_db(uploaded_file.name, ai_analysis)
                    st.success("Asset enriched and written to secure archive database!")
                    st.json(ai_analysis)

with col_gallery:
    st.header("2. Central Digital Archive Explorer")
    
    # Simple filtering UI
    db_records = fetch_drawings()
    
    if not db_records:
        st.info("The archive database is currently empty. Upload a drawing to populate the grid.")
    else:
        # Display data in a structured, scannable table format
        st.subheader("Database Ledger")
        display_data = []
        for r in db_records:
            display_data.append({
                "ID": r[0],
                "Filename": r[1],
                "Type": r[2],
                "Medium": r[3],
                "Era/Style": r[4],
                "Detected Entities": r[5],
                "Architectural Summary": r[6]
            })
        st.dataframe(display_data, use_container_width=True)
        
        # Display visual grid
        st.subheader("Visual Grid")
        grid_cols = st.columns(3)
        for idx, r in enumerate(db_records):
            col = grid_cols[idx % 3]
            img_path = os.path.join("archive_vault", r[1])
            if os.path.exists(img_path):
                col.image(img_path, caption=f"#{r[0]}: {r[1]} ({r[2]})", use_container_width=True)
                with col.expander("View Labels"):
                    st.write(f"**Medium:** {r[3]}")
                    st.write(f"**Elements:** {r[5]}")
