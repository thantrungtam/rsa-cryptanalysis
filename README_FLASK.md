# 🔐 RSA Cryptanalysis Demo - Flask Web Application

**Minh họa phương pháp thám mã tấn công với số mũ công khai nhỏ**

Ứng dụng web Flask đầy đủ chức năng để nghiên cứu và minh họa các lỗ hổng bảo mật của RSA khi sử dụng số mũ công khai nhỏ (e=3).

## 🎯 Mục tiêu

Đáp ứng yêu cầu đề tài nghiên cứu:
- Nghiên cứu lý thuyết về thuật toán RSA
- Minh họa tấn công khi m^e < n
- Mô phỏng tấn công Håstad (Broadcast Attack)
- Cung cấp giao diện trực quan và giải thích chi tiết

## 🚀 Cài đặt và Chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

```bash
python run.py
```

Hoặc:

```bash
python app.py
```

### 3. Truy cập ứng dụng

- **Trang chủ**: http://localhost:5000
- **Lý thuyết**: http://localhost:5000/theory  
- **Demo**: http://localhost:5000/demo

## 📁 Cấu trúc Dự án

```
rsa-cryptanalysis/
├── app.py                 # Ứng dụng Flask chính
├── run.py                 # File khởi chạy
├── requirements.txt       # Dependencies
├── templates/             # HTML templates
│   ├── base.html         # Template cơ sở
│   ├── index.html        # Trang chủ
│   ├── theory.html       # Trang lý thuyết
│   └── demo.html         # Trang demo
└── static/               # Static files
    ├── css/
    │   └── style.css     # CSS chính
    └── js/
        └── app.js        # JavaScript chính
```

## 🔧 Chức năng

### 1. Sinh khóa RSA
- Tạo cặp khóa với số mũ công khai tùy chỉnh (e = 3, 5, 17, 65537)
- Hiển thị đầy đủ thông tin: n, e, d, p, q
- Cảnh báo về tính bảo mật với e nhỏ

### 2. Mã hóa & Giải mã
- Mã hóa bản rõ với khóa công khai
- Giải mã bản mã với khóa riêng
- Phân tích mối quan hệ m^e và n

### 3. Tấn công Khai căn
- Tấn công khi m^e < n
- Hiển thị từng bước chi tiết
- Khôi phục bản rõ bằng căn bậc e

### 4. Tấn công Håstad
- Tạo demo tự động với nhiều khóa
- Sử dụng Định lý Số dư Trung Hoa (CRT)
- Mô phỏng tấn công broadcast

### 5. Lý thuyết
- Giải thích thuật toán RSA
- Phân tích các điều kiện tấn công
- Hướng dẫn biện pháp phòng chống

## 🔬 API Endpoints

### Sinh khóa
```
POST /api/generate_key
Body: {"e": 3, "bits": 1024}
```

### Mã hóa
```
POST /api/encrypt
Body: {"message": "Hello", "n": "...", "e": "3"}
```

### Giải mã
```
POST /api/decrypt
Body: {"ciphertext": "...", "n": "...", "d": "..."}
```

### Tấn công khai căn
```
POST /api/attack_single
Body: {"ciphertext": "...", "n": "...", "e": "3"}
```

### Tấn công Håstad
```
POST /api/attack_hastad
Body: {"ciphertexts": [...], "public_keys": [...]}
```

### Tạo demo Håstad
```
POST /api/generate_hastad_demo
Body: {"message": "Secret", "e": 3, "bits": 1024, "count": 3}
```

## 📚 Hướng dẫn Sử dụng

### Bước 1: Sinh khóa
1. Chọn e = 3 (để dễ tấn công)
2. Chọn độ dài khóa (1024 bit khuyến nghị cho demo)
3. Nhấn "Sinh khóa"
4. Khóa sẽ tự động điền vào các form khác

### Bước 2: Mã hóa
1. Nhập bản rõ ngắn (ví dụ: "Hi", "Hello")
2. Nhấn "Mã hóa"
3. Quan sát cảnh báo nếu m^e < n

### Bước 3: Thử tấn công
1. Chuyển sang tab "Tấn công khai căn"
2. Nhấn "Bắt đầu tấn công"
3. Xem các bước chi tiết

### Bước 4: Demo Håstad
1. Chuyển sang tab "Tấn công Håstad"
2. Nhấn "Tạo Demo" để tự động tạo dữ liệu
3. Nhấn "Bắt đầu tấn công Håstad"
4. Xem quá trình sử dụng CRT

## ⚠️ Lưu ý Bảo mật

- **CHỈ DÙNG CHO MỤC ĐÍCH HỌC TẬP**
- Không sử dụng khóa được tạo trong môi trường thực
- Các tấn công chỉ nhằm mục đích giáo dục
- Hiểu rõ lỗ hổng để thiết kế hệ thống an toàn hơn

## 🛠️ Công nghệ

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Mật mã**: PyCryptodome, SymPy
- **Toán học**: gmpy2, mpmath

## 🎓 Mục tiêu Học tập

### Lý thuyết
- Hiểu thuật toán RSA: sinh khóa, mã hóa, giải mã
- Nắm vai trò của số mũ công khai e
- Phân tích điều kiện tấn công
- Tìm hiểu Định lý Số dư Trung Hoa

### Thực hành
- Triển khai RSA cơ bản
- Mô phỏng tấn công khai căn
- Thực hiện tấn công Håstad
- Đánh giá tính bảo mật

## 📖 Tài liệu Tham khảo

1. **RSA Algorithm**: Rivest, Shamir, Adleman (1977)
2. **Håstad's Attack**: Johan Håstad (1985)
3. **Chinese Remainder Theorem**: Ancient Chinese mathematics
4. **Modern Cryptography**: Various academic sources

## 🤝 Đóng góp

Dự án mở cho việc cải thiện và mở rộng:
- Thêm các phương pháp tấn công khác
- Cải thiện giao diện
- Tối ưu hóa thuật toán
- Thêm tài liệu và ví dụ

## 📄 Giấy phép

Dự án được phân phối dưới giấy phép MIT cho mục đích giáo dục.

---

**Lưu ý**: Đây là công cụ giáo dục. Việc sử dụng để tấn công hệ thống thực tế mà không có sự cho phép là bất hợp pháp. 