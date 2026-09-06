from ultralytics import YOLO

# Tải pre-trained model
model = YOLO('yolov8n.pt') 

# Bắt đầu training
results = model.train(
    data='coco8.yaml',   # Sửa thành đường dẫn thật khi nhóm bạn có dữ liệu
    epochs=3,            # Chạy thử 3 vòng để test lỗi (khi train thật có thể để 50-100)
    imgsz=640,           
    batch=4,             # Hạ số lượng batch xuống để CPU xử lý nhẹ nhàng hơn
    device='cpu'         # Xác nhận chạy bằng CPU
)