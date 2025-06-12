# RSA Attack Demo

Dự án minh họa các cuộc tấn công vào hệ mã hóa RSA khi sử dụng số mũ công khai nhỏ.

## Yêu cầu hệ thống

- Python 3.6 trở lên
- pip (trình quản lý gói Python)

## Cài đặt

1. **Tạo môi trường ảo (khuyến nghị)**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Trên Windows
   source venv/bin/activate  # Trên macOS/Linux
   ```

2. **Cài đặt các thư viện cần thiết**
   ```bash
   pip install -r requirements.txt
   ```

## Cách sử dụng

### 1. Giao diện dòng lệnh (CLI)

Chạy chương trình bằng lệnh:

```bash
python rsa_attack.py
```

Các chức năng chính:
1. Sinh khóa RSA với tham số tùy chỉnh
2. Mã hóa bản rõ
3. Giải mã bản mã
4. Tấn công khai căn khi m^e < n
5. Tấn công Håstad (nhiều người nhận)

### 2. Giao diện đồ họa (GUI)

Chạy giao diện đồ họa bằng lệnh:

```bash
python rsa_attack_gui.py
```

Giao diện gồm các tab chính:
- **Sinh khóa**: Tạo cặp khóa RSA mới
- **Mã hóa/Giải mã**: Thực hiện mã hóa và giải mã thông điệp
- **Tấn công**: Thực hiện các cuộc tấn công RSA
- **Lý thuyết**: Tổng quan về RSA và các phương pháp tấn công

## Mô tả các cuộc tấn công

### 1. Tấn công khai căn (Cube Root Attack)
- Xảy ra khi `m^e < n`
- Kẻ tấn công có thể khôi phục bản rõ bằng cách tính căn bậc e của bản mã

### 2. Tấn công Håstad
- Xảy ra khi cùng một bản rõ được mã hóa với nhiều khóa công khai khác nhau nhưng cùng số mũ e nhỏ
- Sử dụng định lý số dư Trung Hoa (CRT) để khôi phục bản rõ

## Tác giả

Dự án được phát triển bởi [Tên của bạn]

## Giấy phép

Dự án này được phân phối theo giấy phép MIT.
