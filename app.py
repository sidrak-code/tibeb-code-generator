import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import os

# Set page config
st.set_page_config(page_title="🧵 Tibeb Code Generator", layout="centered")

# Custom CSS
st.markdown("""
<style>
  .main {
    background: linear-gradient(135deg, #00571a, #f0a800, #da1a11);
    color: white;
    font-family: 'Segoe UI', sans-serif;
  }
  h1, h2 {
    text-shadow: 1px 1px 3px black;
    color: white !important;
  }
  .stButton>button {
    background: white;
    color: #00571a;
    border-radius: 30px;
    padding: 12px 30px;
    font-weight: bold;
  }
  .stButton>button:hover {
    background: #e0e0e0;
    transform: scale(1.05);
  }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center;'>🧵 ትቤብ ማዕበል</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Tibeb Code Generator – AI-Powered Cultural Design</p>", unsafe_allow_html=True)

# Upload
uploaded_file = st.file_uploader("📁 Upload a photo of a Habesha kemis", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    height, width = img.shape[:2]

    # Crop bottom 20% (Tibeb region)
    tibeb_region = img[height - int(height * 0.2):height, :]
    gray = cv2.cvtColor(tibeb_region, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    _, binary = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)

    # Resize to smaller grid
    scale = 10
    resized = cv2.resize(binary, (width // scale, height // scale), interpolation=cv2.INTER_AREA)

    # Create symbolic pattern
    pattern = []
    for row in resized:
        line = ""
        for pixel in row:
            if pixel > 127:
                line += "X"
            else:
                line += " "
        pattern.append(line.strip())

    # Display
    st.subheader("🔍 Original Tibeb Region")
    st.image(gray, caption="የተቆረጠ ትቤብ ክልል | Cropped Tibeb Region", width=500)

    st.subheader("🧱 Generated Tibeb Code")
    for line in pattern:
        st.text(line)

    # Save and download
    output_text = "\n".join(pattern)
    buf = io.BytesIO()
    buf.write(output_text.encode())
    buf.seek(0)

    st.download_button(
        label="📥 Download Code (.txt)",
        data=buf,
        file_name="tibeb_code.txt",
        mime="text/plain"
    )

st.markdown("<br><center>Made with ❤️ for Ethiopian Heritage</center>", unsafe_allow_html=True)