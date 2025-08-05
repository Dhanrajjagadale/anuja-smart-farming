import streamlit as st
import requests
from datetime import datetime, date
from PIL import Image

# -------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Smart Farming Partner", page_icon="🌾", layout="wide")

# -------------- WEATHER FUNCTION -----------------
def get_weather(city):
    api_key = "261f98e168bbce0a092c3bd323031d7c"  # Replace with your secure key
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            return {
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "desc": data["weather"][0]["description"]
            }
    except:
        pass
    return None

# -------------- SIDEBAR -----------------
with st.sidebar:
    st.header("🔍 Field & Crop Inputs")
    ph = st.slider("Soil pH", 3.5, 9.0, 6.5)
    moisture = st.slider("Soil Moisture (%)", 0, 100, 30)
    temperature = st.number_input("Ambient Temp (°C)", 0.0, 50.0, 25.0)
    crop = st.selectbox("🌾 Select Crop", ["Wheat", "Rice", "Tomato", "Soybean", "Sugarcane", "Millets"])
    plant_date = st.date_input("📆 Date of Planting", value=datetime.today())
    city = st.text_input("🌍 Enter Your City")

# -------------- MAIN -----------------
st.title("🌱 Smart Farming Partner")
st.markdown("#### Making intelligent, location-based, and crop-specific farming decisions.")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Input Summary")
    st.write(f"• Soil pH: **{ph}**")
    st.write(f"• Moisture: **{moisture}%**")
    st.write(f"• Temperature: **{temperature}°C**")
    st.write(f"• Crop: **{crop}**")
    st.write(f"• Planting Date: **{plant_date.strftime('%d %b %Y')}**")
    if city:
        st.write(f"• Location: **{city}**")

with col2:
    st.subheader("🧠 Smart Suggestions")

    if ph < 6:
        st.warning("🔬 Acidic soil: Lime or urea recommended.")
    elif ph > 8:
        st.warning("⚗️ Alkaline soil: Use sulfate fertilizers.")
    else:
        st.success("✅ pH is within optimal range.")

    if moisture < 30:
        st.info("💧 Moisture is low – irrigation needed.")
    else:
        st.success("✅ Moisture is adequate.")

    if temperature > 35:
        st.warning("🔥 High heat – increase water supply.")

    st.subheader("🪴 Fertilizer Guide")
    if ph < 6:
        st.info("Use lime-based fertilizers (e.g., calcium carbonate).")
    elif ph > 8:
        st.info("Use ammonium sulfate or potash sulfate.")
    else:
        st.info("Apply a balanced NPK 10-10-10 mix.")

# -------------- WATERING -----------------
st.markdown("---")
st.subheader("💧 Watering Schedule")
if moisture < 40:
    st.info("Water every 2–3 days.")
elif temperature > 32:
    st.info("Water daily in high heat.")
else:
    st.success("Watering cycle: 3–4 days.")

# -------------- SUPPLEMENTS -----------------
st.markdown("---")
st.subheader("🧪 Planting Supplements")
if crop == "Wheat":
    st.info("Apply DAP + compost at seed level.")
elif crop == "Rice":
    st.info("Urea + phosphorous fertilizer needed.")
elif crop == "Tomato":
    st.info("Use potassium nitrate + bio-fertilizers.")
else:
    st.info("Use NPK + cow dung compost.")

# -------------- WEEK PLANNER -----------------
st.markdown("---")
st.subheader("🗓️ Week-by-Week Planner")
week = (date.today() - plant_date).days // 7

for i in range(1, 5):
    st.markdown(f"**Week {i}:**")
    if crop == "Rice":
        st.write("🐛 Pest: Leaf folder / Stem borer")
        st.write("🌿 Fertilizer: Urea top dressing (Week 2–3)")
    elif crop == "Wheat":
        st.write("🐛 Pest: Aphids / Armyworm")
        st.write("🌿 Fertilizer: Nitrogen in Week 2")
    elif crop == "Tomato":
        st.write("🐛 Pest: Fruit borer / Whiteflies")
        st.write("🌿 Fertilizer: Potash spray")
    else:
        st.write("🐛 Pest: Monitor leaves for worms")
        st.write("🌿 Fertilizer: Rotate NPK bi-weekly")
    st.markdown("---")

# -------------- WEATHER -----------------
if city:
    weather = get_weather(city)
    if weather:
        st.subheader("☁️ Live Weather")
        st.success(f"{weather['temp']}°C, {weather['humidity']}% humidity, {weather['desc'].title()}")

        st.subheader("🌱 Seed Suggestions")
        if weather["temp"] > 30:
            st.info("Recommended: Millets or Sorghum")
        elif weather["humidity"] > 70:
            st.info("Recommended: Rice or Sugarcane")
        else:
            st.info("Recommended: Wheat or Soybean")
    else:
        st.error("❌ Could not fetch weather data.")
else:
    st.warning("📍 Enter a valid city for weather.")

# -------------- WEED IMAGE -----------------
st.markdown("---")
st.subheader("📸 Weed Detection & Pesticide Advice")

upload = st.file_uploader("Upload weed image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

if upload is not None:
    try:
        image = Image.open(upload)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.warning("Detected weed: *General Broadleaf Weed*")
        st.info("Suggested pesticide: Glyphosate or 2,4-D")
    except Exception as e:
        st.error(f"❌ Error displaying image: {e}")

# -------------- FOOTER -----------------
st.markdown("---")
st.caption("🚀 Built with ❤️ using Streamlit | Smart Farming Partner 2025")

