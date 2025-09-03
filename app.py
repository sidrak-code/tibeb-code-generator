import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64
from fpdf2 import FPDF

# Page config
st.set_page_config(page_title="🧵 EthioPattern Studio", layout="wide")

# Custom CSS (Ethiopian colors + modern UI)
st.markdown("""
<style>
  .main {
    background: linear-gradient(135deg, #00571a, #f0a800, #da1a11);
    color: white;
    font-family: 'Segoe UI', sans-serif;
  }
  h1, h2, h3 {
    text-shadow: 1px 1px 3px black;
    color: white !important;
  }
  .stButton>button {
    background: white;
    color: #00571a;
    border-radius: 30px;
    padding: 8px 16px;
    font-weight: bold;
  }
  .stTabs [data-baseweb="tab"] {
    font-size: 18px;
    font-weight: bold;
  }
  .code-output {
    font-family: monospace;
    font-size: 20px;
    line-height: 2;
    background: rgba(0,0,0,0.2);
    padding: 20px;
    border-radius: 10px;
    color: white;
    white-space: pre;
  }
  .sidebar .sidebar-content {
    background: #00330d;
  }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.image("https://i.imgur.com/8B7rCqf.png", width=100)  # Optional: Add logo
st.sidebar.title("🧵 EthioPattern Studio")
page = st.sidebar.radio("Navigate", ["📚 Pattern Library", "📤 Upload & Generate", "✏️ Edit Pattern"])

# Sample Pattern Library (like kal666.pdf)
patterns = {
    "Tibeb Style 1 (kal666)": "X\n\nX\n\nX\n\nVOV V XX X",
    "Amhara Cross Border": "X X X X\n  V V  \nO   O   O\nX X X X",
    "Tigray Zigzag": "V   V   V\n  X   X  \nV   V   V",
    "Oromo Circle Motif": "O   O   O\n  X X X  \nO   O   O"
}

# PDF Export Function
def create_pdf(pattern_code, filename="tibeb_pattern.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=14)
    pdf.set_fill_color(240, 240, 240)
    for line in pattern_code.split('\n'):
        pdf.cell(0, 10, line, ln=True)
    pdf.output(filename)
    return filename

# === PAGE 1: Pattern Library ===
if page == "📚 Pattern Library":
    st.title("📜 Traditional Tibeb Pattern Library")
    st.write("Browse symbolic codes used in Ethiopian textile design.")

    for name, code in patterns.items():
        st.subheader(name)
        st.markdown(f'<div class="code-output">{code}</div>', unsafe_allow_html=True)
        
        # Download buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download (.txt)",
                data=code,
                file_name=f"{name.lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )
        with col2:
            if st.button(f"🖨️ PDF for {name}"):
                pdf_path = create_pdf(code)
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=f"{name}.pdf")

# === PAGE 2: Upload & Generate ===
elif page == "📤 Upload & Generate":
    st.title("📤 Upload Dress Photo → Get Tibeb Code")
    uploaded_file = st.file_uploader("Upload a photo of a Habesha kemis", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        height, width = img.shape[:2]

        # Crop Tibeb
        tibeb_region = img[height - int(height * 0.2):height, :]
        gray = cv2.cvtColor(tibeb_region, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        _, binary = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)

        # Resize to grid
        scale = 10
        resized = cv2.resize(binary, (width // scale, height // scale), interpolation=cv2.INTER_AREA)

        # Generate symbolic pattern
        pattern = []
        for row in resized:
            line = ""
            for pixel in row:
                if pixel > 127:
                    line += "X"
                else:
                    line += " "
            pattern.append(line.strip())
        code_output = "\n".join(pattern)

        # Display
        st.image(gray, caption="Cropped Tibeb Region", width=400)
        st.markdown(f'<div class="code-output">{code_output}</div>', unsafe_allow_html=True)

        # Download
        buf = io.BytesIO()
        buf.write(code_output.encode())
        buf.seek(0)
        st.download_button("📥 Download Code (.txt)", buf, "tibeb_code.txt")

# === PAGE 3: Edit Pattern ===
elif page == "✏️ Edit Pattern":
    st.title("✏️ Symbolic Pattern Editor")
    st.write("Manually create or edit a Tibeb code")

    default_code = st.selectbox("Choose a template", list(patterns.keys()))
    user_code = st.text_area("Edit pattern", value=patterns[default_code], height=300)
    
    st.markdown(f'<div class="code-output">{user_code}</div>', unsafe_allow_html=True)
    
    buf = io.BytesIO()
    buf.write(user_code.encode())
    st.download_button("📥 Save Custom Pattern", buf, "my_tibeb.txt")