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

st.markdown("<h1 class='main-title'>⚙️ CODESYS AI Expert</h1>", unsafe_allow_html=True)
st.markdown("Trợ lý AI chuyên sâu thiết kế cấu trúc phần mềm và lập trình **Structured Text (ST)** trên nền tảng **CODESYS V3.5** (Hỗ trợ Wago, Beckhoff, Schneider, Inovance AM...).")
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
        "Mô tả chi tiết máy tự động hoặc chức năng bạn muốn lập trình:",
        height=300,
        placeholder="Ví dụ:\nHãy hướng dẫn tôi lập trình điều khiển một xi lanh khí nén.\n- Cảm biến hành trình: Sensor_Home, Sensor_End.\n- Nút nhấn: Btn_Auto, Btn_Manual, Btn_Cylinder_Out.\n- Van điện từ: Valve_Out, Valve_Return.\nYêu cầu: Viết theo dạng máy trạng thái (State Machine) dùng lệnh CASE."
    )
    
    generate_btn = st.button("🚀 PHÂN TÍCH & XUẤT CODE", type="primary", use_container_width=True)

with col2:
    st.subheader("💡 Giải pháp & Mã nguồn (CODESYS V3.5)")
    
    if generate_btn:
        if not api_key:
            st.error("⚠️ Hệ thống chưa được cấu hình API Key. Vui lòng thêm key vào file secrets.toml!")
        elif not user_prompt:
            st.warning("⚠️ Vui lòng nhập mô tả bài toán!")
        else:
            with st.spinner(f"Đang thiết kế giải pháp trên nền tảng CODESYS..."):
                try:
                    # Dùng flash để đảm bảo tốc độ cao và không bị dính Quota Limit
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # Prompt Engineering CHUYÊN SÂU CHO CODESYS
                    system_prompt = f"""
                    Bạn là một Chuyên gia Kỹ thuật Phần mềm Tự động hóa (Senior Automation Software Architect), 
                    cực kỳ am hiểu nền tảng CODESYS V3.5 và tiêu chuẩn IEC 61131-3.
                    
                    Người dùng muốn giải quyết bài toán sau: '{user_prompt}'
                    Loại POU ưu tiên: {pou_type}.
                    
                    Hãy xuất kết quả theo ĐÚNG 4 PHẦN sau, sử dụng ngôn ngữ tiếng Việt chuyên nghiệp:
                    
                    ### 1. Hướng dẫn tiếp cận (Architecture Guide)
                    - Giải thích ngắn gọn cách tiếp cận bài toán.
                    - Nên tạo loại POU nào (PRG, FB, FC)? Tại sao?
                    - Cần dùng các thư viện chuẩn nào của CODESYS không (ví dụ Standard.lib cho TON, TOF, R_TRIG...)?
                    
                    ### 2. Khai báo biến (Declaration Part)
                    Viết đoạn code khai báo biến dạng text chuẩn của CODESYS để người dùng có thể copy-paste thẳng vào khung Declaration phía trên của POU.
                    (Sử dụng VAR_INPUT, VAR_OUTPUT, VAR, VAR_IN_OUT... phù hợp).
                    
                    ### 3. Mã nguồn ST (Implementation Part)
                    Viết mã nguồn bằng ngôn ngữ Structured Text. 
                    - Nếu bài toán phức tạp, hãy ưu tiên dùng cấu trúc CASE (State Machine).
                    - Đặt code trong block `pascal` hoặc `iecst`.
                    - Có comment giải thích chi tiết ý nghĩa từng khối lệnh.
                    
                    ### 4. Hướng dẫn sử dụng (Instantiation & Calling)
                    - Hướng dẫn người dùng cách khai báo (Instance) và gọi khối POU này trong chương trình chính (ví dụ PLC_PRG).
                    """
                    
                    response = model.generate_content(system_prompt)
                    st.success("✅ Đã hoàn tất bản thiết kế giải pháp!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi hệ thống: {e}")
    else:
        st.info("Khu vực hiển thị hướng dẫn giải pháp, khai báo biến và mã nguồn. Bấm 'Phân tích & Xuất Code' để bắt đầu.")
