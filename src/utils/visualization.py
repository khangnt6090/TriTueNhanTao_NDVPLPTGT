import cv2
import numpy as np

# Bảng màu riêng cho 4 class chính theo data.yaml của nhóm và dự phòng
CLASS_COLORS = {
    'car': (0, 255, 0),          # Xanh lá (Ô tô)
    'motorbike': (255, 165, 0),  # Xanh dương / Cam (Xe máy)
    'motorcycle': (255, 165, 0), # Dự phòng nhãn COCO
    'bus': (0, 140, 255),        # Cam đậm (Xe buýt)
    'truck': (255, 0, 255),      # Tím hồng (Xe tải)
    'bicycle': (0, 255, 255)     # Vàng (Xe đạp)
}
DEFAULT_COLOR = (200, 200, 200)

def draw_detections(frame, detections, show_conf=True, show_id=True):
    """
    Vẽ Bounding Box, tên phương tiện, độ tin cậy và ID Tracking lên frame.
    detections: danh sách dict [{'box': [x1, y1, x2, y2], 'class_name': str, 'conf': float, 'id': int}]
    """
    annotated_frame = frame.copy()
    counts = {}

    for det in detections:
        x1, y1, x2, y2 = map(int, det['box'])
        class_name = det.get('class_name', 'vehicle')
        conf = det.get('conf', 0.0)
        track_id = det.get('id', None)

        # Đếm số lượng theo class
        counts[class_name] = counts.get(class_name, 0) + 1
        color = CLASS_COLORS.get(class_name.lower(), DEFAULT_COLOR)

        # Vẽ khung Bounding Box
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

        # Tạo chuỗi nhãn
        label_parts = [class_name]
        if show_id and track_id is not None:
            label_parts.insert(0, f"ID:{track_id}")
        if show_conf:
            label_parts.append(f"{conf*100:.1f}%")
        label = " | ".join(label_parts)

        # Vẽ nền và chữ nhãn
        font_scale = 0.5
        thickness = 1
        (label_w, label_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        y_label = max(y1, label_h + 10)
        cv2.rectangle(annotated_frame, (x1, y_label - label_h - 6), (x1 + label_w + 4, y_label + baseline - 4), color, -1)
        cv2.putText(annotated_frame, label, (x1 + 2, y_label - 4), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

    return annotated_frame, counts
