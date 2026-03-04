import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# CẤU HÌNH GIAO DIỆN
# ==========================================
st.set_page_config(page_title="CODESYS AI Expert", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
    .main-title {color: #d10000; font-weight: bold;}
    .stTextArea textarea {font-size: 1.1rem; line-height: 1.5;}
    .step-box {background-color: #f0f2f6; padding: 15px; border-left: 5px solid #d10000; border-radius: 5px; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚙️ CODESYS AI Expert & Tutor</h1>", unsafe_allow_html=True)
st.markdown("Trợ lý AI chuyên sâu thiết kế phần mềm, viết code **Structured Text (ST)** và hướng dẫn thao tác trực tiếp trên nền tảng **CODESYS V3.5**.")
st.markdown("---")

# ==========================================
# LẤY API KEY NGẦM TỪ STREAMLIT SECRETS
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    api_key = None

# ==========================================
# SIDEBAR: CẤU HÌNH
# ==========================================
with st.sidebar:
    if os.path.exists("images/rkv_logo.png"):
        st.image("images/rkv_logo.png", use_container_width=True)
    
    st.header("🛠️ Tùy chọn Kiến trúc")
    pou_type = st.selectbox(
        "AI nên ưu tiên tạo khối nào?",
        ["Tự động quyết định (Khuyên dùng)", "Function Block (FB)", "Function (FC)", "Program (PRG)"]
    )
    
    st.markdown("<div style='text-align: center; color: #888888; font-size: 13px; margin-top: 50px;'>© Bản quyền thuộc về Riken Việt</div>", unsafe_allow_html=True)

# ==========================================
# MAIN AREA
# ==========================================
col1, col2 = st.columns([1.2, 1.8], gap="large")

with col1:
    st.subheader("📝 Yêu cầu bài toán")
    user_prompt = st.text_area(
        "Mô tả chi tiết chức năng bạn muốn lập trình:",
        height=300,
        placeholder="Ví dụ:\nHãy hướng dẫn tôi lập trình một bộ đếm sản phẩm chạy trên băng tải.\n- Sensor: X_Product.\n- Yêu cầu: Đếm số lượng, đếm đến 10 thì bật đèn Y_Full trong 3 giây rồi tự reset bộ đếm."
    )
    
    generate_btn = st.button("🚀 PHÂN TÍCH & XUẤT CODE", type="primary", use_container_width=True)

with col2:
    st.subheader("💡 Giải pháp & Hướng dẫn (CODESYS V3.5)")
    
    if generate_btn:
        if not api_key:
            st.error("⚠️ Hệ thống chưa được cấu hình API Key. Vui lòng thêm key vào file secrets.toml!")
        elif not user_prompt:
            st.warning("⚠️ Vui lòng nhập mô tả bài toán!")
        else:
            with st.spinner(f"Đang thiết kế giải pháp và trích xuất tài liệu hướng dẫn CODESYS..."):
                try:
                    # Dùng flash để đảm bảo tốc độ cao và không bị dính Quota Limit
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # Prompt Engineering CẤP ĐỘ GIA SƯ (TUTOR) CHO CODESYS
                    system_prompt = f"""
                    Bạn là một Chuyên gia Kỹ thuật Phần mềm Tự động hóa (Senior Automation Architect) và là Giảng viên đào tạo CODESYS V3.5.
                    
                    Người dùng muốn giải quyết bài toán sau: '{user_prompt}'
                    Loại POU ưu tiên: {pou_type}.
                    
                    Hãy xuất kết quả theo ĐÚNG 5 PHẦN sau, trình bày cực kỳ dễ hiểu, từng bước một:
                    
                    ### 1. 🖱️ Hướng dẫn thao tác trên phần mềm (GUI Step-by-step)
                    - Hướng dẫn người dùng MỞ PHẦN MỀM CODESYS và click chuột vào đâu để tạo khối code này.
                    - Cụ thể: Click chuột phải vào 'Application' -> Chọn 'Add Object' -> 'POU'...
                    - Đặt tên khối là gì? Chọn Type là gì (Program/FB/FC)? Chọn Implementation Language là gì (Structured Text - ST)?
                    
                    ### 2. 🧠 Phân tích Thuật toán
                    - Giải thích ngắn gọn cách tiếp cận bài toán.
                    - Cần dùng các block chuẩn nào (như TON, CTU, R_TRIG từ Standard.lib)?
                    
                    ### 3. 📋 Khai báo biến (Declaration Part)
                    - Cung cấp đoạn text khai báo biến để người dùng COPY và PASTE thẳng vào KHUNG PHÍA TRÊN của POU trong CODESYS.
                    - Dùng đúng chuẩn: VAR_INPUT, VAR_OUTPUT, VAR...
                    
                    ### 4. 💻 Mã nguồn ST (Implementation Part)
                    - Cung cấp mã nguồn Structured Text để COPY và PASTE vào KHUNG PHÍA DƯỚI của POU.
                    - Chú ý: Cú pháp CODESYS yêu cầu gọi biến instance của Timer/Counter đúng chuẩn (VD: T1(IN:= , PT:= ); ).
                    - Comment giải thích chi tiết trong code.
                    
                    ### 5. ⚙️ Cấu hình chạy thực tế (Calling & Task Configuration)
                    - Hướng dẫn cách gọi khối này trong chương trình chính (thường là PLC_PRG).
                    - Nhắc nhở người dùng kiểm tra 'Task Configuration' -> 'MainTask' xem đã có PLC_PRG trong đó chưa để code được quét (Cyclic).
                    """
                    
                    response = model.generate_content(system_prompt)
                    st.success("✅ Đã hoàn tất bản thiết kế và hướng dẫn!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi hệ thống: {e}")
    else:
        st.info("Nhập yêu cầu bên trái. Hệ thống sẽ hướng dẫn bạn từng cú click chuột trên CODESYS và xuất mã nguồn chuẩn.")
