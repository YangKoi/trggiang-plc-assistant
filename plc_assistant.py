import streamlit as st
import google.generativeai as genai
import os
# ==========================================
# CẤU HÌNH GIAO DIỆN
# ==========================================
st.set_page_config(page_title="Trg Giang - PLC AI Assistant", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .main-title {color: #0056b3; font-weight: bold;}
    .stTextArea textarea {font-size: 1.1rem; line-height: 1.5;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🤖 Trợ Lý Trí Tuệ Nhân Tạo: Lập Trình PLC</h1>", unsafe_allow_html=True)
st.markdown("Hỗ trợ sinh mã tự động bằng ngôn ngữ **Structured Text (ST / SCL)** cho các khối hàm (FB/FC).")
st.markdown("---")

# ==========================================
# LẤY API KEY NGẦM TỪ STREAMLIT SECRETS
# ==========================================
try:
    # Hệ thống sẽ tự động tìm key có tên là GEMINI_API_KEY trong cấu hình bảo mật
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    api_key = None

# ==========================================
# SIDEBAR: CẤU HÌNH HÃNG PLC
# ==========================================
with st.sidebar:
    if os.path.exists("images/rkv_logo.png"):
        st.image("images/rkv_logo.png", use_container_width=True)
    
    st.header("🎛️ Nền tảng đích")
    plc_brand = st.selectbox(
        "Chọn hãng PLC:",
        ["Siemens (TIA Portal - SCL)", "Mitsubishi (GX Works 3 - ST)", "Inovance (AutoShop - ST)"]
    )
    
    st.markdown("<div style='text-align: center; color: #888888; font-size: 13px; margin-top: 50px;'>© Bản quyền thuộc về trggiang</div>", unsafe_allow_html=True)

# ==========================================
# MAIN AREA: NHẬP YÊU CẦU & XUẤT KẾT QUẢ
# ==========================================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📝 Yêu cầu bài toán")
    user_prompt = st.text_area(
        "Mô tả chi tiết chức năng bạn muốn lập trình:",
        height=250,
        placeholder="Ví dụ:\nViết một Function Block điều khiển 2 bơm luân phiên.\n- Input: Start, Stop, Reset, Thoi_Gian_Chuyen_Doi.\n- Output: Bom_1_Run, Bom_2_Run.\n- Yêu cầu: Bơm tự động chuyển đổi theo thời gian. Khi một bơm báo lỗi, tự động chuyển sang bơm còn lại."
    )
    
    generate_btn = st.button("🚀 XUẤT CODE (GENERATE)", type="primary", use_container_width=True)

with col2:
    st.subheader("💻 Kết quả (SCL / ST)")
    
    if generate_btn:
        if not api_key:
            st.error("⚠️ Hệ thống chưa được cấu hình API Key. Vui lòng báo cho Admin!")
        elif not user_prompt:
            st.warning("⚠️ Vui lòng nhập mô tả bài toán!")
        else:
            with st.spinner(f"Đang phân tích cú pháp cho {plc_brand}..."):
                try:
                    # Cấu hình AI với API Key đã giấu
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # Prompt Engineering cốt lõi ngầm định
                    system_prompt = f"""
                    Bạn là một Kỹ sư Tự động hóa (Automation Engineer) cấp cao, cực kỳ am hiểu về ngôn ngữ lập trình Structured Text (ST/SCL).
                    Hãy viết một Function Block (FB) hoặc Function (FC) để giải quyết yêu cầu dưới đây của người dùng.
                    
                    Nền tảng đích: {plc_brand}. (Phải viết đúng chuẩn cú pháp của phần mềm hãng này).
                    Yêu cầu: {user_prompt}
                    
                    Quy tắc trình bày:
                    1. Bảng Khai báo biến (Tên biến, Kiểu dữ liệu, Loại: Input/Output/InOut/Static/Temp, Mô tả).
                    2. Mã nguồn (Chỉ dùng SCL/ST, đặt trong block code, có comment giải thích chi tiết).
                    3. Lưu ý ngắn gọn về cách gọi hàm này.
                    """
                    
                    response = model.generate_content(system_prompt)
                    st.success("✅ Thành công!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Đã xảy ra lỗi hệ thống: {e}")
    else:
        st.info("Khu vực hiển thị mã nguồn và danh sách biến. Bấm 'Xuất Code' để bắt đầu.")
