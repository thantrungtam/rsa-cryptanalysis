from flask import Flask, render_template, request, jsonify
import json
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Crypto.Hash import SHA256
from sympy import mod_inverse, integer_nthroot, isprime, nextprime, gcd
import base64
import os
import random
import sys

# Tăng giới hạn độ dài chuỗi số nguyên để xử lý số lớn trong RSA
sys.set_int_max_str_digits(50000)

app = Flask(__name__)

class RSAService:
    """Lớp service xử lý các thao tác RSA và tấn công"""
    
    @staticmethod
    def generate_rsa_key(e=3, bits=1024):
        """Tạo cặp khóa RSA với số mũ công khai e"""
        try:
            # Nếu bits >= 1024, sử dụng thư viện Crypto bình thường
            if bits >= 1024:
                while True:
                    key = RSA.generate(bits, e=e)
                    if key.e == e:
                        return {
                            'success': True,
                            'n': str(key.n),
                            'e': str(key.e),
                            'd': str(key.d),
                            'p': str(key.p),
                            'q': str(key.q),
                            'bits': bits
                        }
            else:
                # Tạo khóa tùy chỉnh cho bits < 1024 (cho mục đích demo)
                return RSAService._generate_custom_rsa_key(e, bits)
                
        except Exception as ex:
            return {'success': False, 'error': str(ex)}
    
    @staticmethod
    def _generate_custom_rsa_key(e=3, bits=512):
        """Tạo khóa RSA tùy chỉnh cho bits nhỏ (dành cho demo)"""
        try:
            from math import gcd
            
            # Tính bit length cho p và q
            p_bits = bits // 2
            q_bits = bits - p_bits
            
            max_attempts = 100  # Giới hạn số lần thử để tránh vòng lặp vô tận
            
            for attempt in range(max_attempts):
                # Sinh số nguyên tố p
                while True:
                    p = random.getrandbits(p_bits)
                    p |= (1 << (p_bits - 1))  # Đảm bảo bit cao nhất là 1
                    p |= 1  # Đảm bảo số lẻ
                    if isprime(p):
                        break
                
                # Sinh số nguyên tố q khác p
                while True:
                    q = random.getrandbits(q_bits)
                    q |= (1 << (q_bits - 1))  # Đảm bảo bit cao nhất là 1
                    q |= 1  # Đảm bảo số lẻ
                    if isprime(q) and q != p:
                        break
                
                # Tính n và phi(n)
                n = p * q
                phi_n = (p - 1) * (q - 1)
                
                # Kiểm tra điều kiện gcd(e, phi_n) = 1
                if gcd(e, phi_n) == 1:
                    # Tính d = e^(-1) mod phi(n)
                    d = mod_inverse(e, phi_n)
                    
                    return {
                        'success': True,
                        'n': str(n),
                        'e': str(e),
                        'd': str(d),
                        'p': str(p),
                        'q': str(q),
                        'bits': bits
                    }
                
                # Nếu không thỏa mãn, thử lại với p, q khác
            
            # Nếu sau max_attempts lần vẫn không tìm được khóa phù hợp
            return {
                'success': False, 
                'error': f'Không thể tạo khóa RSA với e={e} sau {max_attempts} lần thử. Hãy thử với e khác hoặc bits lớn hơn.'
            }
            
        except Exception as ex:
            return {'success': False, 'error': f'Lỗi tạo khóa tùy chỉnh: {str(ex)}'}
    
    @staticmethod
    def encrypt_message(message, n, e, input_type='text', padding_type='raw'):
        """Mã hóa tin nhắn với khóa công khai RSA"""
        try:
            n = int(n)
            e = int(e)
            
            # Xử lý input theo loại
            if input_type == 'integer':
                try:
                    message_int = int(message)
                    original_display = f"Số nguyên: {message}"
                except ValueError:
                    return {'success': False, 'error': 'Input không phải là số nguyên hợp lệ.'}
            else:  # text
                message_bytes = message.encode('utf-8')
                original_display = f"Văn bản: \"{message}\""
            
            # Xử lý padding
            if padding_type == 'raw':
                if input_type == 'text':
                    message_int = bytes_to_long(message_bytes)
                if message_int >= n:
                    return {'success': False, 'error': 'Thông điệp quá lớn so với modulus n.'}
                
                # Raw RSA encryption
                ciphertext = pow(message_int, e, n)
                me_value = pow(message_int, e)
                
                return {
                    'success': True,
                    'ciphertext': str(ciphertext),
                    'message_int': str(message_int),
                    'original_display': original_display,
                    'input_type': input_type,
                    'padding_type': padding_type,
                    'comparison': f"m^{e} = {message_int}^{e} = {me_value:,} {'<' if me_value < n else '>='} n = {n:,}",
                    'is_vulnerable': me_value < n,
                    'padding_info': 'Không sử dụng padding (Raw RSA - dễ bị tấn công)'
                }
                
            elif padding_type == 'pkcs1_v1_5':
                # PKCS#1 v1.5 padding
                key = RSA.construct((n, e))
                cipher = PKCS1_v1_5.new(key)
                ciphertext_bytes = cipher.encrypt(message_bytes)
                ciphertext = bytes_to_long(ciphertext_bytes)
                
                return {
                    'success': True,
                    'ciphertext': str(ciphertext),
                    'message_int': 'N/A (sử dụng padding)',
                    'original_display': original_display,
                    'input_type': input_type,
                    'padding_type': padding_type,
                    'comparison': 'Sử dụng PKCS#1 v1.5 padding - an toàn hơn',
                    'is_vulnerable': False,
                    'padding_info': 'PKCS#1 v1.5 - thêm random padding để chống tấn công'
                }
                
            elif padding_type == 'oaep':
                # OAEP padding
                key = RSA.construct((n, e))
                cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
                ciphertext_bytes = cipher.encrypt(message_bytes)
                ciphertext = bytes_to_long(ciphertext_bytes)
                
                return {
                    'success': True,
                    'ciphertext': str(ciphertext),
                    'message_int': 'N/A (sử dụng padding)',
                    'original_display': original_display,
                    'input_type': input_type,
                    'padding_type': padding_type,
                    'comparison': 'Sử dụng OAEP padding - rất an toàn',
                    'is_vulnerable': False,
                    'padding_info': 'OAEP (Optimal Asymmetric Encryption Padding) - chuẩn bảo mật cao nhất'
                }
            
        except Exception as ex:
            return {'success': False, 'error': str(ex)}
    
    @staticmethod
    def decrypt_message(ciphertext, n, d, padding_type='raw', e=None):
        """Giải mã bản mã với khóa riêng RSA"""
        try:
            n = int(n)
            d = int(d)
            ciphertext = int(ciphertext)
            
            if padding_type == 'raw':
                message_int = pow(ciphertext, d, n)
                message = long_to_bytes(message_int).decode()
                return {'success': True, 'message': message, 'message_int': str(message_int), 'padding_type': padding_type}
                
            elif padding_type == 'pkcs1_v1_5':
                if e is None:
                    e = 65537  # Default value
                key = RSA.construct((n, int(e), d))
                cipher = PKCS1_v1_5.new(key)
                ciphertext_bytes = long_to_bytes(ciphertext)
                message_bytes = cipher.decrypt(ciphertext_bytes, None)
                if message_bytes is None:
                    return {'success': False, 'error': 'Giải mã PKCS#1 v1.5 thất bại'}
                message = message_bytes.decode('utf-8')
                return {'success': True, 'message': message, 'message_int': 'N/A', 'padding_type': padding_type}
                
            elif padding_type == 'oaep':
                if e is None:
                    e = 65537  # Default value
                key = RSA.construct((n, int(e), d))
                cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
                ciphertext_bytes = long_to_bytes(ciphertext)
                message_bytes = cipher.decrypt(ciphertext_bytes)
                message = message_bytes.decode('utf-8')
                return {'success': True, 'message': message, 'message_int': 'N/A', 'padding_type': padding_type}
                
        except Exception as ex:
            return {'success': False, 'error': str(ex)}
    
    @staticmethod
    def validate_coprime_moduli(moduli):
        """Kiểm tra các moduli có đôi một là số nguyên tố cùng nhau (coprime)"""
        validation_result = {
            'valid': True,
            'errors': [],
            'gcd_matrix': [],
            'steps': []
        }
        
        n = len(moduli)
        validation_result['steps'].append(f"🔍 KIỂM TRA COPRIME: Kiểm tra {n} moduli")
        validation_result['steps'].append("📚 ĐIỀU KIỆN: Các moduli phải đôi một nguyên tố cùng nhau (gcd = 1)")
        
        # Tạo ma trận GCD để hiển thị
        gcd_matrix = []
        for i in range(n):
            gcd_row = []
            for j in range(n):
                if i == j:
                    gcd_value = moduli[i]  # Đường chéo chính là chính modulus đó
                    gcd_row.append(f"n{i+1}")
                else:
                    gcd_value = gcd(moduli[i], moduli[j])
                    gcd_row.append(str(gcd_value))
                    
                    # Kiểm tra điều kiện coprime
                    if i < j and gcd_value != 1:  # Chỉ kiểm tra phần tam giác trên để tránh lặp
                        validation_result['valid'] = False
                        validation_result['errors'].append(
                            f"❌ gcd(n{i+1}, n{j+1}) = gcd({moduli[i]}, {moduli[j]}) = {gcd_value} ≠ 1"
                        )
                        validation_result['steps'].append(
                            f"⚠️ PHÁT HIỆN LỖI: Modulus {i+1} và {j+1} không nguyên tố cùng nhau"
                        )
                    elif i < j:
                        validation_result['steps'].append(
                            f"✅ gcd(n{i+1}, n{j+1}) = 1 - OK"
                        )
            gcd_matrix.append(gcd_row)
        
        validation_result['gcd_matrix'] = gcd_matrix
        
        if validation_result['valid']:
            validation_result['steps'].append("🎯 KẾT LUẬN: Tất cả các moduli đều nguyên tố cùng nhau")
            validation_result['steps'].append("✅ CHINESE REMAINDER THEOREM có thể áp dụng")
        else:
            validation_result['steps'].append("❌ KẾT LUẬN: Một số moduli không nguyên tố cùng nhau")
            validation_result['steps'].append("⛔ CHINESE REMAINDER THEOREM KHÔNG thể áp dụng")
            validation_result['steps'].append("💡 GIẢI PHÁP: Cần sử dụng các moduli từ những nguồn khác nhau")
        
        return validation_result

    @staticmethod
    def chinese_remainder_theorem(congruences, verbose=False):
        """Giải hệ phương trình đồng dư bằng định lý số dư Trung Hoa"""
        steps = []
        total = 0
        product = 1
        
        for _, mod in congruences:
            product *= mod
        
        steps.append(f"Tích các modulus (N): {product}")
        
        for i, (remainder, mod) in enumerate(congruences):
            p = product // mod
            inv = mod_inverse(p, mod)
            contribution = remainder * p * inv
            total += contribution
            steps.append(f"Phần tử {i+1}: remainder={remainder}, mod={mod}, p={p}, inv={inv}, contribution={contribution}")
        
        result = total % product
        steps.append(f"Kết quả CRT: {result}")
        
        return result, steps
    
    @staticmethod
    def low_exponent_attack_single(ciphertext, e, n):
        """Tấn công khai căn khi m^e < n"""
        try:
            ciphertext = int(ciphertext)
            e = int(e)
            n = int(n)
            
            steps = []
            steps.append(f"Bản mã: {ciphertext}")
            steps.append(f"Giải phương trình m^{e} = {ciphertext} (mod {n}) với m^e < n")
            steps.append(f"Vì m^{e} < n, ta có thể khai căn trực tiếp: m = ∛{ciphertext}")
            
            m_root, exact = integer_nthroot(ciphertext, e)
            steps.append(f"Kết quả khai căn bậc {e}: {m_root}, chính xác: {exact}")
            
            if not exact:
                return {'success': False, 'error': 'Không tìm được căn bậc e chính xác. Có thể bản mã hoặc khóa không hợp lệ.', 'steps': steps}
            
            try:
                message = long_to_bytes(m_root).decode()
            except:
                message = str(long_to_bytes(m_root))
            
            steps.append(f"Chuyển đổi số nguyên thành chuỗi: {message}")
            
            return {'success': True, 'message': message, 'steps': steps, 'recovered_m': str(m_root)}
        except Exception as ex:
            return {'success': False, 'error': str(ex)}
    
    @staticmethod
    def hastad_attack(ciphertexts, public_keys, padding_type='raw', original_message=None):
        """Tấn công Håstad khi cùng bản rõ gửi tới nhiều người"""
        try:
            # Chuyển đổi input thành số nguyên
            ciphertexts = [int(c) for c in ciphertexts]
            public_keys = [(int(key['n']), int(key['e'])) for key in public_keys]
            
            e = public_keys[0][1]  # Giả sử tất cả có cùng e
            moduli = [n for n, _ in public_keys]
            
            steps = []
            steps.append(f"Số mũ công khai e = {e}")
            steps.append(f"Số lượng bản mã: {len(ciphertexts)}")
            steps.append(f"Loại padding được sử dụng: {padding_type}")
            
            # Validation: Kiểm tra các moduli có coprime không
            steps.append("\n" + "="*50)
            validation = RSAService.validate_coprime_moduli(moduli)
            steps.extend(validation['steps'])
            steps.append("="*50 + "\n")
            
            # Nếu validation thất bại, trả về lỗi
            if not validation['valid']:
                error_message = "VALIDATION THẤT BẠI: " + "; ".join(validation['errors'])
                return {
                    'success': False, 
                    'error': error_message,
                    'steps': steps,
                    'validation_failed': True,
                    'gcd_matrix': validation['gcd_matrix'],
                    'errors': validation['errors']
                }
            
            # Kiểm tra padding
            if padding_type != 'raw':
                steps.append(f"⚠️ CẢNH BÁO: Đang thử tấn công với padding {padding_type}")
                steps.append("Tấn công Håstad thường chỉ hiệu quả với Raw RSA, nhưng sẽ thử nghiệm...")
            
            # Tạo hệ phương trình đồng dư
            congruences = [(c, n) for c, (n, _) in zip(ciphertexts, public_keys)]
            
            for i, (c, n) in enumerate(congruences):
                steps.append(f"Phương trình {i+1}: m^{e} ≡ {c} (mod {n})")
            
            # Giải bằng CRT
            steps.append("Áp dụng định lý số dư Trung Hoa:")
            result, crt_steps = RSAService.chinese_remainder_theorem(congruences, verbose=True)
            steps.extend(crt_steps)
            
            # Khai căn
            steps.append(f"Khai căn bậc {e} của {result}:")
            m_root, exact = integer_nthroot(result, e)
            steps.append(f"Kết quả khai căn bậc {e}: {m_root}, chính xác: {exact}")
            
            if not exact:
                if padding_type != 'raw':
                    steps.append("❌ THẤT BẠI: Không thể khai căn chính xác")
                    steps.append(f"🔍 NGUYÊN NHÂN: Padding {padding_type} đã làm thay đổi cấu trúc dữ liệu")
                    steps.append("📚 GIẢI THÍCH: Với padding, cùng message sẽ tạo ra các ciphertext khác nhau")
                    steps.append("   → Chinese Remainder Theorem không áp dụng được")
                    steps.append("   → Đây chính là lý do padding được thiết kế để chống tấn công này!")
                    return {'success': False, 'error': 'Tấn công thất bại do padding chống bảo vệ', 'steps': steps, 'padding_protected': True}
                return {'success': False, 'error': 'Không tìm được căn bậc e chính xác.', 'steps': steps}
            
            # Xử lý kết quả dựa trên padding type
            if padding_type == 'raw':
                try:
                    message = long_to_bytes(m_root).decode()
                    steps.append(f"✅ THÀNH CÔNG: Bản rõ thu được: {message}")
                    
                    # So sánh với original message nếu có
                    if original_message and message == original_message:
                        steps.append(f"🎯 XÁC NHẬN: Kết quả khớp với bản rõ gốc!")
                    elif original_message:
                        steps.append(f"⚠️ CẢNH BÁO: Kết quả '{message}' khác với bản rõ gốc '{original_message}'")
                        
                    return {'success': True, 'message': message, 'steps': steps, 'recovered_m': str(m_root)}
                    
                except UnicodeDecodeError:
                    message_bytes = long_to_bytes(m_root)
                    steps.append(f"✅ THÀNH CÔNG: Khôi phục được dữ liệu (binary): {message_bytes}")
                    return {'success': True, 'message': str(message_bytes), 'steps': steps, 'recovered_m': str(m_root)}
                    
            else:
                # Với padding, cần giải mã padding
                steps.append(f"🔄 Đang thử giải mã padding {padding_type}...")
                try:
                    # Đây chỉ là attempt - thường sẽ fail với padded data
                    raw_bytes = long_to_bytes(m_root)
                    
                    if padding_type == 'pkcs1_v1_5':
                        steps.append("🔍 Đang tìm kiếm cấu trúc PKCS#1 v1.5: 0x00 0x02 [PS] 0x00 [MESSAGE]")
                        # Thử tìm pattern PKCS#1 v1.5
                        if len(raw_bytes) >= 11 and raw_bytes[0:2] == b'\x00\x02':
                            # Tìm separator 0x00
                            try:
                                sep_idx = raw_bytes.index(b'\x00', 2)
                                message = raw_bytes[sep_idx+1:].decode()
                                steps.append(f"✅ THÀNH CÔNG: Tìm thấy message trong padding: {message}")
                                return {'success': True, 'message': message, 'steps': steps, 'recovered_m': str(m_root)}
                            except (ValueError, UnicodeDecodeError):
                                pass
                    
                    # Nếu không giải được padding
                    steps.append(f"❌ THẤT BẠI: Không thể giải mã padding {padding_type}")
                    steps.append("🔍 NGUYÊN NHÂN: Dữ liệu thu được không có cấu trúc padding hợp lệ")
                    steps.append("📚 KẾT LUẬN: Padding đã chống được tấn công Håstad thành công!")
                    
                    return {'success': False, 'error': f'Không thể giải mã padding {padding_type}', 
                           'steps': steps, 'padding_protected': True, 'raw_recovered': str(m_root)}
                    
                except Exception as decode_ex:
                    steps.append(f"❌ LỖI khi giải mã: {str(decode_ex)}")
                    return {'success': False, 'error': f'Lỗi giải mã padding: {str(decode_ex)}', 'steps': steps}
                    
        except Exception as ex:
            return {'success': False, 'error': str(ex)}

# Routes
@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/theory')
def theory():
    """Trang lý thuyết"""
    return render_template('theory.html')

@app.route('/demo')
def demo():
    """Trang demo"""
    return render_template('demo.html')

# API Endpoints
@app.route('/api/generate_key', methods=['POST'])
def api_generate_key():
    """API sinh khóa RSA"""
    data = request.get_json()
    e = data.get('e', 3)
    bits = data.get('bits', 1024)
    
    result = RSAService.generate_rsa_key(e=e, bits=bits)
    return jsonify(result)

@app.route('/api/encrypt', methods=['POST'])
def api_encrypt():
    """API mã hóa"""
    data = request.get_json()
    message = data.get('message', '')
    n = data.get('n', '')
    e = data.get('e', '')
    input_type = data.get('input_type', 'text')
    padding_type = data.get('padding_type', 'raw')
    
    result = RSAService.encrypt_message(message, n, e, input_type, padding_type)
    return jsonify(result)

@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    """API giải mã"""
    data = request.get_json()
    ciphertext = data.get('ciphertext', '')
    n = data.get('n', '')
    d = data.get('d', '')
    e = data.get('e', None)
    padding_type = data.get('padding_type', 'raw')
    
    result = RSAService.decrypt_message(ciphertext, n, d, padding_type, e)
    return jsonify(result)

@app.route('/api/attack_single', methods=['POST'])
def api_attack_single():
    """API tấn công khai căn đơn"""
    data = request.get_json()
    ciphertext = data.get('ciphertext', '')
    e = data.get('e', '')
    n = data.get('n', '')
    
    result = RSAService.low_exponent_attack_single(ciphertext, e, n)
    return jsonify(result)

@app.route('/api/attack_hastad', methods=['POST'])
def api_attack_hastad():
    """API tấn công Håstad"""
    data = request.get_json()
    ciphertexts = data.get('ciphertexts', [])
    public_keys = data.get('public_keys', [])
    padding_type = data.get('padding_type', 'raw')
    original_message = data.get('original_message', None)
    
    result = RSAService.hastad_attack(ciphertexts, public_keys, padding_type, original_message)
    return jsonify(result)

@app.route('/api/generate_hastad_demo', methods=['POST'])
def api_generate_hastad_demo():
    """API tạo demo tấn công Håstad"""
    data = request.get_json()
    message = data.get('message', 'Hello')
    e = data.get('e', 3)
    bits = data.get('bits', 1024)
    count = data.get('count', 3)
    input_type = data.get('input_type', 'text')
    padding_type = data.get('padding_type', 'raw')
    
    try:
        # Tạo nhiều cặp khóa với validation coprime
        keys = []
        ciphertexts = []
        encryption_details = []
        moduli = []
        
        max_retries = 50  # Số lần thử tối đa để tránh vòng lặp vô tận
        current_retry = 0
        
        for i in range(count):
            retry_count = 0
            while retry_count < max_retries:
                key_result = RSAService.generate_rsa_key(e=e, bits=bits)
                if not key_result['success']:
                    return jsonify({'success': False, 'error': key_result['error']})
                
                new_n = int(key_result['n'])
                
                # Kiểm tra modulus mới có coprime với các modulus đã có không
                is_coprime_with_existing = True
                for existing_n in moduli:
                    if gcd(new_n, existing_n) != 1:
                        is_coprime_with_existing = False
                        break
                
                if is_coprime_with_existing:
                    # Modulus hợp lệ, thêm vào danh sách
                    moduli.append(new_n)
                    
                    # Mã hóa cùng một message với input_type và padding_type
                    encrypt_result = RSAService.encrypt_message(message, key_result['n'], key_result['e'], input_type, padding_type)
                    if not encrypt_result['success']:
                        return jsonify({'success': False, 'error': encrypt_result['error']})
                    
                    keys.append({
                        'n': key_result['n'],
                        'e': key_result['e'],
                        'd': key_result['d'],
                        'index': i + 1
                    })
                    ciphertexts.append(encrypt_result['ciphertext'])
                    
                    # Lưu thông tin mã hóa để phân tích
                    encryption_details.append({
                        'key_index': i + 1,
                        'ciphertext': encrypt_result['ciphertext'],
                        'is_vulnerable': encrypt_result.get('is_vulnerable', False) if padding_type == 'raw' else False,
                        'padding_info': encrypt_result.get('padding_info', ''),
                        'message_int': encrypt_result.get('message_int', 'N/A')
                    })
                    break
                else:
                    retry_count += 1
                    current_retry += 1
            
            if retry_count >= max_retries:
                return jsonify({
                    'success': False, 
                    'error': f'Không thể tạo được khóa thứ {i+1} coprime với các khóa trước đó sau {max_retries} lần thử. Hãy thử với bits lớn hơn hoặc giảm số lượng khóa.'
                })
        
        # Validation cuối cùng để chắc chắn
        validation = RSAService.validate_coprime_moduli(moduli)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': 'VALIDATION THẤT BẠI: Một số moduli không coprime mặc dù đã kiểm tra khi sinh.',
                'validation_errors': validation['errors']
            })
        
        # Phân tích khả năng tấn công
        attack_analysis = {
            'can_attack': padding_type == 'raw',
            'reason': 'Raw RSA - có thể tấn công' if padding_type == 'raw' 
                     else f'Padding {padding_type} chống được tấn công Håstad',
            'padding_effectiveness': {
                'raw': 'Không có bảo vệ - dễ bị tấn công',
                'pkcs1_v1_5': 'Random padding làm mỗi lần mã hóa tạo ra kết quả khác nhau',
                'oaep': 'Hash-based padding với random elements - cực kỳ an toàn'
            }.get(padding_type, 'Unknown padding'),
            'educational_note': 'Demo này cho phép bạn thấy tại sao padding quan trọng trong RSA'
        }
        
        return jsonify({
            'success': True,
            'message': message,
            'keys': keys,
            'ciphertexts': ciphertexts,
            'input_type': input_type,
            'padding_type': padding_type,
            'encryption_details': encryption_details,
            'attack_analysis': attack_analysis,
            'coprime_validation': {
                'validated': True,
                'generation_retries': current_retry,
                'moduli_count': len(moduli),
                'note': 'Tất cả moduli đã được kiểm tra và đảm bảo coprime để có thể áp dụng CRT'
            }
        })
    except Exception as ex:
        return jsonify({'success': False, 'error': str(ex)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 