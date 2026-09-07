import streamlit as st
import cv2
import tempfile
import os
import numpy as np
import pandas as pd
from PIL import Image
from ultralytics import YOLO

# Import module visualization đã xây dựng
try:
    from src.utils.visualization import draw_detections, CLASS_COLORS
except ImportError:
    # Dự phòng nếu chạy độc lập
    from utils.visualization import draw_detections, CLASS_COLORS

# Thiết lập trang giao diện
st.set_page_config(page_title="Hệ Thống Nhận Diện Phương Tiện", layout="wide", page_icon="🚦")

st.markdown("""
    <h2 style='text-align: center; color: #1E88E5;'>HỆ THỐNG NHẬN DIỆN VÀ PHÂN LOẠI PHƯƠNG TIỆN GIAO THÔNG</h2>
    <p style='text-align: center; color: gray;'>Đồ án Trí Tuệ Nhân Tạo - Dataset: Vehicle_Danang_2025</p>
    <hr>
""", unsafe_allow_html=True)

# --- SIDEBAR CẤU HÌNH ---
st.sidebar.header("⚙️ Cấu hình hệ thống")

model_path = st.sidebar.text_input("Đường dẫn file Model (.pt):", value="yolov8n.pt")
confidence_thresh = st.sidebar.slider("Ngưỡng tin cậy (Confidence):", min_value=0.1, max_value=1.0, value=0.4, step=0.05)

st.sidebar.subheader("👁️ Tùy chọn hiển thị")
show_conf = st.sidebar.checkbox("Hiển thị độ tin cậy (%)", value=True)
show_id = st.sidebar.checkbox("Hiển thị ID Tracking", value=True)

input_mode = st.sidebar.radio("Nguồn đầu vào:", ["Hình ảnh", "Video", "Webcam/Camera"])

@st.cache_resource
def load_yolo_model(path):
    return YOLO(path)

try:
    with st.spinner("Đang khởi tạo mô hình..."):
        model = load_yolo_model(model_path)
    st.sidebar.success("✅ Đã nạp mô hình thành công!")
except Exception as e:
    st.sidebar.error(f"❌ Không thể tải mô hình: {e}")
    st.stop()

# --- XỬ LÝ NGUỒN 1: HÌNH ẢNH ---
if input_mode == "Hình ảnh":
    st.subheader("🖼️ Nhận diện phương tiện từ Hình ảnh")
    uploaded_file = st.file_uploader("Chọn file ảnh (jpg, png, jpeg):", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="Ảnh gốc đầu vào", use_container_width=True)

        if st.button("🚀 Bắt đầu nhận diện", type="primary"):
            with st.spinner("Đang xử lý hình ảnh..."):
                results = model.predict(source=image, conf=confidence_thresh)
                
                detections = []
                for box in results[0].boxes:
                    cls_id = int(box.cls[0].item())
                    class_name = model.names[cls_id]
                    conf = float(box.conf[0].item())
                    xyxy = box.xyxy[0].tolist()
                    detections.append({'box': xyxy, 'class_name': class_name, 'conf': conf})

                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                annotated_img, counts = draw_detections(img_cv, detections, show_conf, show_id=False)
                annotated_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)

                with col2:
                    st.image(annotated_rgb, caption="Kết quả nhận diện", use_container_width=True)

            st.markdown("### 📊 Thống kê phương tiện phát hiện:")
            if counts:
                df_counts = pd.DataFrame(list(counts.items()), columns=["Loại phương tiện", "Số lượng"])
                st.dataframe(df_counts, hide_index=True)
            else:
                st.info("Không phát hiện phương tiện nào với ngưỡng tin cậy đã chọn.")

# --- XỬ LÝ NGUỒN 2: VIDEO ---
elif input_mode == "Video":
    st.subheader("🎥 Nhận diện & Tracking phương tiện từ Video")
    video_file = st.file_uploader("Tải lên file video (.mp4, .avi, .mov):", type=["mp4", "avi", "mov"])

    if video_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())

        cap = cv2.VideoCapture(tfile.name)
        st_frame = st.empty()
        st_metrics = st.empty()
        btn_stop = st.button("⏹️ Dừng xử lý")

        while cap.isOpened() and not btn_stop:
            ret, frame = cap.read()
            if not ret:
                break

            # Tracking tích hợp ByteTrack
            results = model.track(source=frame, persist=True, conf=confidence_thresh, tracker="bytetrack.yaml")
            
            detections = []
            if results[0].boxes is not None:
                for box in results[0].boxes:
                    cls_id = int(box.cls[0].item())
                    class_name = model.names[cls_id]
                    conf = float(box.conf[0].item())
                    xyxy = box.xyxy[0].tolist()
                    track_id = int(box.id[0].item()) if box.id is not None else None
                    detections.append({'box': xyxy, 'class_name': class_name, 'conf': conf, 'id': track_id})

            annotated_frame, counts = draw_detections(frame, detections, show_conf, show_id)
            annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            st_frame.image(annotated_rgb, channels="RGB", use_container_width=True)

            summary_text = " | ".join([f"{k}: {v}" for k, v in counts.items()])
            st_metrics.info(f"**Phương tiện trong khung hình:** {summary_text if summary_text else 'Không có'}")

        cap.release()

# --- XỬ LÝ NGUỒN 3: WEBCAM ---
elif input_mode == "Webcam/Camera":
    st.subheader("📷 Nhận diện trực tiếp qua Webcam")
    img_file_buffer = st.camera_input("Chụp ảnh từ Camera để nhận diện:")

    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)
        results = model.predict(source=image, conf=confidence_thresh)
        
        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0].item())
            class_name = model.names[cls_id]
            conf = float(box.conf[0].item())
            xyxy = box.xyxy[0].tolist()
            detections.append({'box': xyxy, 'class_name': class_name, 'conf': conf})

        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        annotated_img, counts = draw_detections(img_cv, detections, show_conf, show_id=False)
        annotated_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
        
        st.image(annotated_rgb, caption="Kết quả nhận diện từ Camera", use_container_width=True)
        if counts:
            df_counts = pd.DataFrame(list(counts.items()), columns=["Loại phương tiện", "Số lượng"])
            st.dataframe(df_counts, hide_index=True)
