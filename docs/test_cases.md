# KỊCH BẢN KIỂM THỬ HỆ THỐNG (TEST CASES & RESULTS)
* **Đề tài:** Nhận diện và phân loại phương tiện giao thông
* **Tập dữ liệu kiểm thử:** `Vehicle_Danang_2025`
* **Người thực hiện:** Thành viên 5 (UI, Visualization & Testing)
* **Các lớp đối tượng (Classes):** `car` (0), `motorbike` (1), `bus` (2), `truck` (3)

## 1. Danh sách các trường hợp kiểm thử (Test Matrix)

| Test ID | Kịch bản kiểm thử | Dữ liệu đầu vào | Kết quả mong đợi | Kết quả thực tế | Đánh giá |
|:---|:---|:---|:---|:---|:---:|
| **TC-01** | Kiểm tra nhận diện ảnh tĩnh rõ nét | Ảnh ban ngày, ô tô và xe máy đi đúng làn | Nhận diện đúng bounding box và phân loại chính xác `car`, `motorbike` | Bắt đúng 100% các xe có kích thước chuẩn | **PASS** |
| **TC-02** | Kiểm tra phân loại xe cỡ lớn (`bus`, `truck`) | Ảnh/video xe buýt và xe tải trên đường phố Đà Nẵng | Phân biệt chính xác giữa `bus` và `truck` | Bounding box bao phủ đầy đủ thân xe, không bị cắt đôi | **PASS** |
| **TC-03** | Kiểm tra video giao thông giờ cao điểm | Video ngã tư mật độ phương tiện dày đặc | Duy trì bounding box, phân loại được các xe đi sát nhau | Nhận diện tốt phần lớn phương tiện, một số xe máy bị che khuất | **PASS** |
| **TC-04** | Kiểm tra điều kiện ánh sáng yếu / Ban đêm | Video giao thông ban đêm, đèn đường và đèn xe chói | Vẫn nhận diện được các phương tiện có đèn sáng | Nhận diện đạt ~80%, các vùng quá tối có thể giảm độ tin cậy | **PASS** |
| **TC-05** | Kiểm tra tính năng Object Tracking (ID) | Video phương tiện di chuyển liên tục qua khung hình | ID xe không bị nhảy hoặc hoán đổi giữa các xe | ByteTrack duy trì ID ổn định xuyên suốt quỹ đạo | **PASS** |
| **TC-06** | Kiểm tra ngoại lệ: File đầu vào sai định dạng | Tải lên file text hoặc file không hợp lệ | Báo lỗi rõ ràng trên UI, ứng dụng không bị văng | Giao diện hiển thị cảnh báo lỗi thân thiện | **PASS** |

## 2. Phân tích các trường hợp biên và lỗi thường gặp (Edge Cases)
1. **Xe bị che khuất (Occlusion):** Xe máy đi sát sau xe buýt/xe tải thường bị khuất một phần, làm giảm confidence score.
2. **Xe ở khoảng cách xa (Small Objects):** Các phương tiện ở cuối góc camera có kích thước quá nhỏ, cần đặt ngưỡng confidence phù hợp (~0.3 - 0.4) để không bỏ sót.
3. **Hiện tượng ID Switch khi Tracking:** Khi hai xe máy vượt nhau ở cự ly gần, ID có thể bị tráo đổi tạm thời trước khi ổn định lại.
