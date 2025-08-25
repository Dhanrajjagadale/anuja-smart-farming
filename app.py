# app.py
# ANUJA – Smart Farming Partner
# Streamlit app with logo support, safer weather key handling, and robust UX.

from __future__ import annotations

import os
import base64
from pathlib import Path
from datetime import date, timedelta
from typing import Optional, Dict, Any

import requests
from PIL import Image
import streamlit as st


# ----------------- CONSTANTS & PATHS -----------------
APP_TITLE = "ANUJA - Smart Farming Partner"
ASSETS_DIR = Path("assets")
LOGO_PATH = ASSETS_DIR / "logo.png"
WEATHER_TTL_SECONDS = 600  # 10 minutes cache


# ----------------- UTILITIES -----------------
def load_logo(path: Path) -> Optional[Image.Image]:
    if not path.exists():
        return None
    try:
        return Image.open(path)
    except Exception:
        return None


def get_openweather_key() -> str:
    # Prefer Streamlit secrets; fallback to env var
    key = st.secrets.get("api_keys", {}).get("openweather", "")
    if not key:
        key = os.getenv("OPENWEATHERMAP_KEY", "")
    return key


@st.cache_data(ttl=WEATHER_TTL_SECONDS, show_spinner=False)
def fetch_current_weather(city: str, api_key: str) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        main = data.get("main") or {}
        weather_list = data.get("weather") or []
        desc = (weather_list[0].get("description") if weather_list else "") or ""
        return {
            "temp": main.get("temp"),
            "humidity": main.get("humidity"),
            "desc": desc,
            "city": data.get("name", city),
            "country": (data.get("sys") or {}).get("country", ""),
        }
    except Exception:
        return None


def seed_recommendation(temp: Optional[float], humidity: Optional[float]) -> str:
    if temp is not None and temp > 30:
        return "Millets or Sorghum"
    if humidity is not None and humidity > 70:
        return "Rice or Sugarcane"
    return "Wheat or Soybean"


def week_range_text(start_week: int, offset: int) -> str:
    # Shows "Week N" relative to planting (N = start_week + offset)
    return f"Week {start_week + offset}"


# ----------------- SETUP: CONFIG & LOGO -----------------
logo_img = load_logo(LOGO_PATH)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=logo_img if logo_img else "🌾",
    layout="wide",
)

# Optional: top banner or sidebar logo
with st.sidebar:
    if logo_img:
        st.image(logo_img, use_container_width=True)
    st.header("🔍 Field & Crop Inputs")


# ----------------- SIDEBAR INPUTS -----------------
ph = st.sidebar.slider("Soil pH", 3.5, 9.0, 6.5)
moisture = st.sidebar.slider("Soil Moisture (%)", 0, 100, 30)
temperature = st.sidebar.number_input("Ambient Temp (°C)", 0.0, 50.0, 25.0)

crop = st.sidebar.selectbox(
    "🌾 Select Crop",
    ["Wheat", "Rice", "Tomato", "Soybean", "Sugarcane", "Millets"],
)

# IMPORTANT: use `date` (not `datetime`) for Streamlit date_input default
plant_date = st.sidebar.date_input("📆 Date of Planting", value=date.today())
city = st.sidebar.text_input("🌍 Enter Your City (for Weather)")

# ----------------- MAIN TITLE -----------------
st.title("🌱 ANUJA – Your Smart Farming Partner")
st.markdown("#### Making intelligent, location-based, and crop-specific farming decisions.")
st.markdown("---")


# ----------------- SMART SUGGESTIONS -----------------
colA, colB = st.columns(2)

with colA:
    st.subheader("📥 Input Summary")
    st.write(f"• Soil pH: **{ph}**")
    st.write(f"• Moisture: **{moisture}%**")
    st.write(f"• Temp: **{temperature} °C**")
    st.write(f"• Crop: **{crop}**")
    st.write(f"• Planting Date: **{plant_date.strftime('%d %b %Y')}**")
    if city:
        st.write(f"• City: **{city}**")

with colB:
    st.subheader("🧠 Smart Suggestions")

    # pH analysis
    if ph < 6:
        st.warning("🔬 Soil acidic: consider treating with lime.")
    elif ph > 8:
        st.warning("⚗️ Soil alkaline: sulfate-based fertilizers recommended.")
    else:
        st.success("✅ pH is balanced.")

    # Moisture analysis
    if moisture < 30:
        st.info("💧 Moisture low: irrigation recommended.")
    else:
        st.success("✅ Moisture adequate.")

    # Temperature analysis
    if temperature > 35:
        st.warning("🔥 High temp: monitor crop water needs.")

    st.subheader("🪴 Fertilizer Guide")
    if ph < 6:
        st.info("Apply lime-based amendment (e.g., agricultural lime / calcium carbonate).")
    elif ph > 8:
        st.info("Use sulfate fertilizers (e.g., ammonium sulfate, potassium sulfate).")
    else:
        st.info("Balanced NPK (e.g., 10-10-10) is suitable.")

# ----------------- WATERING SCHEDULE -----------------
st.markdown("---")
st.subheader("💧 Watering Schedule")

if moisture < 40:
    st.info("💧 Suggest watering **every 2–3 days** based on crop and soil type.")
elif temperature > 32:
    st.info("☀️ High temp: water lightly **daily**, preferably early morning.")
else:
    st.success("✅ Current moisture and temperature support a **3–4 day** watering cycle.")

# ----------------- PLANTING SUPPLEMENTS -----------------
st.markdown("---")
st.subheader("🧪 Required Supplements at Planting")

if crop == "Wheat":
    st.info("Apply DAP + organic compost at seed level.")
elif crop == "Rice":
    st.info("Use urea + phosphorus-based fertilizer.")
elif crop == "Tomato":
    st.info("Add potassium nitrate and bio-fertilizers before planting.")
elif crop == "Sugarcane":
    st.info("Apply farmyard manure + NPK with emphasis on nitrogen.")
elif crop == "Soybean":
    st.info("Use phosphorus-rich fertilizer and rhizobium inoculant where available.")
elif crop == "Millets":
    st.info("Light N application with organic compost; avoid over-fertilization.")
else:
    st.info("Use a standard NPK blend with organic compost.")

# ----------------- FUTURE WEEK PLANNER -----------------
st.markdown("---")
st.subheader("🗓️ Future Pest & Fertilizer Planner")

# Weeks since planting; never negative
weeks_since = max(0, (date.today() - plant_date).days // 7)

for i in range(1, 5):
    st.markdown(f"**{week_range_text(weeks_since + 1, i - 1)}:**")
    if crop == "Rice":
        st.write("🐛 Pest: Leaf folder / Stem borer — monitor leaf whorls and tillers.")
        st.write("🌿 Fertilizer: Top dress with urea in weeks 2–3; maintain standing water depth.")
    elif crop == "Wheat":
        st.write("🐛 Pest: Aphids / Armyworm — inspect earheads and flag leaves.")
        st.write("🌿 Fertilizer: Apply nitrogen in split doses (e.g., week 2).")
    elif crop == "Tomato":
        st.write("🐛 Pest: Fruit borer / Whiteflies — consider traps and regular scouting.")
        st.write("🌿 Fertilizer: Potash foliar spray recommended; maintain calcium levels.")
    elif crop == "Sugarcane":
        st.write("🐛 Pest: Early shoot borer — monitor for dead hearts.")
        st.write("🌿 Fertilizer: Nitrogen top dressing; ensure adequate potassium.")
    elif crop == "Soybean":
        st.write("🐛 Pest: Leaf-eating caterpillars — check defoliation levels.")
        st.write("🌿 Fertilizer: Phosphorus maintenance; avoid excess nitrogen.")
    elif crop == "Millets":
        st.write("🐛 Pest: Shoot fly / Stem borer — monitor seedlings and whorls.")
        st.write("🌿 Fertilizer: Light N in splits; keep soil moisture even.")
    else:
        st.write("🐛 Pest: General leaf feeders — watch leaves closely.")
        st.write("🌿 Fertilizer: Rotate NPK every 2 weeks.")
    st.markdown("---")

# ----------------- WEATHER & SEED SUGGESTION -----------------
if city.strip():
    OWM_KEY = get_openweather_key()
    weather = fetch_current_weather(city.strip(), OWM_KEY)

    st.subheader("☁️ Live Weather Report")
    if not OWM_KEY:
        st.warning(
            "No OpenWeatherMap key found. Add it to **.streamlit/secrets.toml** "
            'under `[api_keys] openweather="..."` or set the `OPENWEATHERMAP_KEY` env var.'
        )
    if weather:
        city_label = weather["city"]
        country = f", {weather['country']}" if weather.get("country") else ""
        desc = (weather["desc"] or "").title()
        st.success(f"{city_label}{country}: {weather['temp']}°C, {weather['humidity']}% humidity, {desc}")

        st.subheader("🌱 Suggested Seeds")
        st.info(f"Recommend: **{seed_recommendation(weather['temp'], weather['humidity'])}**")
    else:
        st.error("❌ Could not fetch weather for that location.")
else:
    st.warning("📍 Enter a valid city to detect weather.")

# ----------------- WEED IMAGE UPLOAD -----------------
st.markdown("---")
st.subheader("📸 Weed Detection & Pesticide Advice")

upload = st.file_uploader("Upload weed image (jpg/png)", type=["jpg", "jpeg", "png"])
if upload:
    st.image(upload, caption="Uploaded Image", use_container_width=True)
    # Placeholder guidance (no ML model wired here)
    st.warning("Detected weed: *General Broadleaf Weed* (placeholder)")
    st.info("Suggested pesticide: Consult local agri extension. Common options include glyphosate or 2,4-D depending on crop stage and label directions.")

# ----------------- FOOTER -----------------
st.markdown("---")
st.caption("🚀 Built with ❤️ using Streamlit | Project ANUJA – Smart Agriculture 2025")
