import streamlit as st
import requests
import base64
from datetime import date

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="AI Travel Stylist", page_icon="✈️", layout="wide")

st.title("✈️ AI Travel Stylist")
st.subheader("วางแผนการแต่งกายสำหรับการเดินทางด้วย AI")

# ส่วนรับ API Key
with st.sidebar:
    st.header("🔑 กำหนดค่า API Key")
    openai_api_key = st.text_input("OpenAI API Key (Vision)", type="password")
    weather_api_key = st.text_input("OpenWeatherMap API Key (Optional)", type="password")

# ฟังก์ชันดึงสภาพอากาศ
def get_weather(city, api_key):
    if not api_key:
        return None
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=th"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            return f"อุณหภูมิประมาณ {data['main']['temp']}°C ({data['weather'][0]['description']})"
    except:
        pass
    return None

# ฟอร์มรับข้อมูล
col1, col2 = st.columns(2)

with col1:
    destination = st.text_input("ปลายทาง (เช่น Tokyo)", "")
    d1 = st.date_input("วันเริ่มต้น", date.today())
    d2 = st.date_input("วันสิ้นสุด", date.today())
    activities = st.multiselect("กิจกรรมที่วางแผนไว้", [
        "เดินชมเมือง", "เที่ยวทะเล", "ปีนเขา/เดินป่า", "งานเลี้ยง/ดินเนอร์", "เยี่ยมชมวัด/สถานที่ศักดิ์สิทธิ์", "ช้อปปิ้ง", "ทำกิจกรรมกลางแจ้ง"
    ])

with col2:
    uploaded_file = st.file_uploader("อัปโหลดรูปภาพชุดแต่งกายของคุณ", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="รูปภาพที่อัปโหลด", use_column_width=True)

# ปุ่มส่งข้อมูลให้ AI วิเคราะห์
if st.button("✨ รับคำแนะนำจาก AI", use_container_width=True):
    if not openai_api_key:
        st.error("กรุณากรอก OpenAI API Key ในแถบด้านข้างก่อนครับ")
    elif not destination or not uploaded_file or not activities:
        st.error("กรุณากรอกข้อมูลและอัปโหลดรูปภาพให้ครบถ้วน")
    else:
        with st.spinner("กำลังวิเคราะห์ข้อมูลสภาพอากาศและชุดแต่งกาย..."):
            weather_text = get_weather(destination, weather_api_key) or "คาดการณ์ตามฤดูกาลปกติ"
            
            # แปลงภาพเป็น Base64
            bytes_data = uploaded_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode('utf-8')
            
            prompt = f"""
            ฉันกำลังจะเดินทางไปเที่ยวที่ {destination} ในวันที่ {d1} ถึง {d2}
            ข้อมูลสภาพอากาศ: {weather_text}
            กิจกรรมที่วางแผนจะทำคือ: {', '.join(activities)}
            
            ในฐานะสไตลิสต์ผู้เชี่ยวชาญ กรุณาวิเคราะห์ชุดในภาพนี้อย่างละเอียด และแนะนำร้านค้าในไทย (UNIQLO TH, Lazada, Shopee) ที่ซื้อหรือเช่าได้
            """
            
            apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={openai_api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": uploaded_file.type, "data": base64_image}}
                    ]
                }]
            }
            
            try:
                response = requests.post(apiUrl, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    st.success("วิเคราะห์สำเร็จ!")
                    st.markdown(result['candidates'][0]['content']['parts'][0]['text'])
                else:
                    st.error(f"เกิดข้อผิดพลาดจาก API (Code: {response.status_code})")
            except Exception as e:
                st.error(f"ไม่สามารถเชื่อมต่อได้: {e}")