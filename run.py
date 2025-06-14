#!/usr/bin/env python3
"""
RSA Cryptanalysis Demo - Web Application Runner
Khởi chạy ứng dụng Flask để minh họa các phương pháp tấn công RSA
"""

from app import app
import os

if __name__ == '__main__':
    # Thiết lập cấu hình
    app.config['SECRET_KEY'] = 'rsa-demo-secret-key-for-development-only'
    app.config['DEBUG'] = True
    
    # Thông tin khởi chạy
    print("=" * 60)
    print("🔐 RSA Cryptanalysis Demo")
    print("Minh họa phương pháp thám mã tấn công với số mũ công khai nhỏ")
    print("=" * 60)
    print("\n📋 Các chức năng chính:")
    print("• Sinh khóa RSA với tham số tùy chỉnh")
    print("• Mã hóa và giải mã bản rõ")
    print("• Tấn công khai căn khi m^e < n")
    print("• Tấn công Håstad (Broadcast Attack)")
    print("• Lý thuyết và giải thích chi tiết")
    
    print("\n🌐 Truy cập ứng dụng tại:")
    print("• Trang chủ: http://localhost:5000")
    print("• Lý thuyết: http://localhost:5000/theory")
    print("• Demo: http://localhost:5000/demo")
    
    print("\n⚠️ Lưu ý: Chỉ sử dụng cho mục đích học tập và nghiên cứu!")
    print("=" * 60)
    
    # Khởi chạy ứng dụng
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Ứng dụng đã được dừng.")
    except Exception as e:
        print(f"\n❌ Lỗi khởi chạy ứng dụng: {e}")
        print("Hãy kiểm tra:")
        print("• Các thư viện đã được cài đặt: pip install -r requirements.txt")
        print("• Port 5000 không bị sử dụng bởi ứng dụng khác")
        print("• Quyền truy cập mạng và firewall") 