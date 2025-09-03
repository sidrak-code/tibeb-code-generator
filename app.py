import streamlit as st
import cv2
import numpy as np
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import base64
import random

# Page config
st.set_page_config(page_title="🧵 Tibeb AI Studio", layout="centered")

# Custom CSS
st.markdown("""
<style>
  .main {
    background: linear-gradient(135deg, #00571a, #f0a800, #da1a11);
    color: white;
  }
  h1, h2 {
    text-shadow: 1px 1px 3px black;
    color: white !important;
  }
  .stButton>button {
    background: white;
    color: #00571a;
    border-radius: 30px;
    font-weight: bold;
  }
  .code-output {
    font-family: monospace;
    font-size: 20px;
    line-height: 2;
    background: rgba(0,0,0,0.3);
    padding: 20px;
    border-radius: 10px;
    color: white;
    white-space: pre;
    text-align: center;
  }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center;'>🧵 ትቤብ ማዕበል</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>AI Tool to Reverse & Generate Tibeb Blueprints</p>", unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["🧬 AI Generate New Pattern", "🔍 Reverse Engineer from Photo"])

# === TAB 1: AI GENERATE ===
with tab1:
    st.subheader("Create a New Tibeb Sketch (Like kal666.pdf)")

    if st.button("✨ Generate New Pattern"):
        # Simulate kal666.pdf style
        top = "X\n\nX\n\nX\n"
        choices = [
            "VOV V XX X",
            "V V O V XX",
            "O V V O X X X",
            "V O V V XX X",
            "X X V O V V",
            "V V V O O X"
        ]
        bottom = random.choice(choices)
        generated = top + bottom

        st.markdown(f'<div class="code-output">{generated}</div>', unsafe_allow_html=True)

        # Download
        b64 = base64.b64encode(generated.encode()).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="tibeb_new.txt">📥 Download Text</a>'
        st.markdown(href, unsafe_allow_html=True)

# === TAB 2: REVERSE ENGINEER ===
with tab2:
    uploaded_file = st.file_uploader("📸 Upload a photo of a finished Tibeb", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        height, width = img.shape[:2]

        tibeb_region = img[height - int(height * 0.2):height, :]
        gray = cv2.cvtColor(tibeb_region, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

        def classify_shape(contour):
            area = cv2.contourArea(contour)
            if area < 100: return None
            approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
            if len(approx) == 3: return "triangle"
            elif len(approx) == 4: return "square"
            else:
                (x, y), r = cv2.minEnclosureCircle(contour)
                circ = area / (np.pi * r * r) if r > 0 else 0
                return "circle" if circ > 0.7 else "cross"

        # Create SVG
        svg = Element('svg', {'xmlns': 'http://www.w3.org/2000/svg', 'width': '800', 'height': '100', 'viewBox': '0 0 800 100'})
        x_pos = 20
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            shape = classify_shape(cnt)
            cy = 50
            if shape == "triangle":
                points = f"{x_pos},{cy-15} {x_pos+10},{cy+15} {x_pos+20},{cy-15}"
                SubElement(svg, 'polyline', {'points': points, 'fill': 'none', 'stroke': 'black', 'stroke-width': '2'})
                x_pos += 30
            elif shape == "square":
                SubElement(svg, 'rect', {'x': str(x_pos), 'y': str(cy-15), 'width': '20', 'height': '30', 'fill': 'none', 'stroke': 'black', 'stroke-width': '2'})
                x_pos += 30
            elif shape == "circle":
                SubElement(svg, 'circle', {'cx': str(x_pos+10), 'cy': str(cy), 'r': '15', 'fill': 'none', 'stroke': 'black', 'stroke-width': '2'})
                x_pos += 30
            elif shape == "cross":
                SubElement(svg, 'line', {'x1': str(x_pos), 'y1': str(cy), 'x2': str(x_pos+20), 'y2': str(cy), 'stroke': 'black', 'stroke-width': '2'})
                SubElement(svg, 'line', {'x1': str(x_pos+10), 'y1': str(cy-10), 'y2': str(cy+10), 'stroke': 'black', 'stroke-width': '2'})
                x_pos += 30

        # Convert to string
        rough = tostring(svg, 'utf-8')
        reparsed = minidom.parseString(rough)
        svg_str = reparsed.toprettyxml(indent="  ")

        st.image(gray, caption="Cropped Tibeb Region", width=500)
        st.subheader("Generated SVG for CNC")
        b64_svg = base64.b64encode(svg_str.encode()).decode()
        href = f'<a href="data:image/svg+xml;base64,{b64_svg}" download="tibeb_shapes.svg"><button>📥 Download SVG</button></a>'
        st.markdown(href, unsafe_allow_html=True)

st.markdown("<br><center>Preserving and generating the hidden code of Ethiopian textile art</center>", unsafe_allow_html=True)
