# app.py
import streamlit as st
import requests
from datetime import datetime, date
from PIL import Image
from ultralytics import YOLO
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Smart Farming Partner",
    page_icon="🌾",
    layout="wide"
)

# Load Logo (optional)
try:
    logo = Image.open("assets/anuja_logo.png")
    st.sidebar.image(logo, width=150)
except Exception:
    st.sidebar.write("🌱 Smart Farming Partner")

# Load YOLO Model
MODEL_PATH = "weights/weed_best.pt"
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    st.error(f"⚠️ Could not load YOLO model: {e}")
    model = None

# ---------------- WEATHER API ----------------
def get_weather(city: str):
    """Fetch weather data from OpenWeatherMap"""
    api_key = st.secrets.get("weather_api", "YOUR_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return {
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "desc": data["weather"][0]["description"]
            }
    except Exception as e:
        st.error(f"Weather fetch error: {e}")
    return None

# ---------------- SIDEBAR INPUTS ----------------
with st.sidebar:
    st.header("🔍 Field & Crop Inputs")
    ph = st.slider("Soil pH", 3.5, 9.0, 6.5)
    moisture = st.slider("Soil Moisture (%)", 0, 100, 30)
    temperature = st.number_input("Ambient Temp (°C)", 0.0, 50.0, 25.0)
    crop = st.selectbox("🌾 Select Crop", ["Wheat", "Rice", "Tomato", "Soybean", "Sugarcane", "Millets"])
    plant_date = st.date_input("📆 Planting Date", value=datetime.today())
    city = st.text_input("🌍 Your City")

# ---------------- MAIN APP ----------------
st.title("🌱 Smart Farming Partner")
st.markdown("#### Location-based, crop-specific guidance for smarter farming.")
st.markdown("---")

col1, col2 = st.columns(2)

# ---- Input Summary ----
with col1:
    st.subheader("📥 Input Summary")
    st.write(f"• Soil pH: **{ph}**")
    st.write(f"• Moisture: **{moisture}%**")
    st.write(f"• Temp: **{temperature}°C**")
    st.write(f"• Crop: **{crop}**")
    st.write(f"• Date: **{plant_date.strftime('%d %b %Y')}**")
    if city:
        st.write(f"• Location: **{city}**")

# ---- Smart Suggestions ----
with col2:
    st.subheader("🧠 Smart Suggestions")
    if ph < 6:
        st.warning("🔬 Soil acidic: Apply lime or urea.")
    elif ph > 8:
        st.warning("⚗️ Soil alkaline: Use sulfate fertilizers.")
    else:
        st.success("✅ pH is optimal.")

    if moisture < 30:
        st.info("💧 Moisture low – irrigate urgently.")
    else:
        st.success("✅ Moisture sufficient.")

    if temperature > 35:
        st.warning("🔥 High temp – increase watering.")

    st.subheader("🪴 Fertilizer Guide")
    st.info("Recommended: NPK mix or crop-specific blend.")

# ---------------- WATERING ----------------
st.markdown("---")
st.subheader("💧 Watering Schedule")
if moisture < 40:
    st.info("Water every 2–3 days.")
elif temperature > 32:
    st.info("High heat: Daily watering advised.")
else:
    st.success("Watering cycle: 3–4 days.")

# ---------------- SUPPLEMENTS ----------------
st.markdown("---")
st.subheader("🧪 Planting Supplements")
supplements = {
    "Wheat": "Use DAP + compost.",
    "Rice": "Urea + phosphorus fertilizer.",
    "Tomato": "Potassium nitrate + bio-fertilizer.",
    "Soybean": "Use Rhizobium inoculant + NPK.",
    "Sugarcane": "Nitrogen-rich fertilizer + organic compost.",
    "Millets": "Low-input: NPK + farmyard manure."
}
st.info(supplements.get(crop, "Use NPK + cow dung compost."))

# ---------------- PLANNER ----------------
st.markdown("---")
st.subheader("🗓️ Crop Planner")
week = (date.today() - plant_date).days // 7
for i in range(1, 5):
    st.markdown(f"**Week {i}:**")
    st.write("🐛 Pest: Monitor weekly")
    st.write("🌿 Fertilizer: Rotate NPK")
    st.markdown("---")

# ---------------- WEATHER ----------------
if city:
    weather = get_weather(city)
    if weather:
        st.subheader("☁️ Weather Update")
        st.success(f"{weather['temp']}°C | {weather['humidity']}% humidity | {weather['desc'].title()}")
        st.subheader("🌱 Seed Suggestions")
        if weather["temp"] > 30:
            st.info("Millets or Sorghum recommended.")
        elif weather["humidity"] > 70:
            st.info("Rice or Sugarcane ideal.")
        else:
            st.info("Try Wheat or Soybean.")
    else:
        st.error("❌ Weather data not available.")

# ---------------- WEED DETECTION ----------------
st.markdown("---")
st.subheader("📸 Weed Detection & Pesticide Advice")

upload = st.file_uploader("Upload weed image", type=["jpg", "jpeg", "png"])
if upload is not None and model:
    try:
        image = Image.open(upload).convert("RGB")
        image_np = np.array(image)
        results = model(image_np)[0]
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if results.boxes:
            for box in results.boxes:
                cls_id = int(box.cls[0].item())
                label = model.names[cls_id]
                confidence = box.conf[0].item()
                st.success(f"Detected: **{label}** ({confidence:.2f})")

                if "broadleaf" in label.lower():
                    st.info("Recommended pesticide: Glyphosate or 2,4-D")
                elif "grass" in label.lower():
                    st.info("Recommended pesticide: Atrazine or Pendimethalin")
                else:
                    st.info("Use crop-specific herbicide.")
        else:
            st.warning("⚠️ No weeds detected.")
    except Exception as e:
        st.error(f"❌ Detection failed: {e}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("🚀 Smart Farming Partner · YOLOv8 Edition · Built with ❤️ using Streamlit")
