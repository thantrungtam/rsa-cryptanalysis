from flask import Flask, render_template, request, jsonify
import json
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
from sympy import mod_inverse, integer_nthroot
import base64

app = Flask(__name__)

class RSAService:
    """Lớp service xử lý các thao tác RSA và tấn công"""
    
    @staticmethod
    def generate_rsa_key(e=3, bits=1024):
        """Tạo cặp khóa RSA với số mũ công khai e"""
        try:
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
        except Exception as ex:
            return {'success': False, 'error': str(ex)}
    
    @staticmethod
    def encrypt_message(message, n, e):
        """Mã hóa tin nhắn với khóa công khai RSA"""
        try:
            n = int(n)
            e = int(e)
            message_int = bytes_to_long(message.encode())
            
            if message_int >= n:
                return {'success': False, 'error': 'Thông điệp quá dài so với modulus n.'}
            
            ciphertext = pow(message_int, e, n)
            return {
                'success': True,
                'ciphertext': str(ciphertext),
                'message_int': str(message_int),
                'comparison': f"m^e = {message_int}^{e} = {pow(message_int, e)} {'<' if pow(message_int, e) < n else '>='} n = {n}"
            }
        except Exception as ex:
            return {'success': False, 'error': str(ex)}
    
    @staticmethod
    def decrypt_message(ciphertext, n, d):
        """Giải mã bản mã với khóa riêng RSA"""
        try:
            n = int(n)
            d = int(d)
            ciphertext = int(ciphertext)
            
            message_int = pow(ciphertext, d, n)
            message = long_to_bytes(message_int).decode()
            return {'success': True, 'message': message, 'message_int': str(message_int)}
        except Exception as ex:
            return {'success': False, 'error': str(ex)}
    
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
    def hastad_attack(ciphertexts, public_keys):
        """Tấn công Håstad khi cùng bản rõ gửi tới nhiều người"""
        try:
            # Chuyển đổi input thành số nguyên
            ciphertexts = [int(c) for c in ciphertexts]
            public_keys = [(int(key['n']), int(key['e'])) for key in public_keys]
            
            e = public_keys[0][1]  # Giả sử tất cả có cùng e
            
            steps = []
            steps.append(f"Số mũ công khai e = {e}")
            steps.append(f"Số lượng bản mã: {len(ciphertexts)}")
            
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
                return {'success': False, 'error': 'Không tìm được căn bậc e chính xác.', 'steps': steps}
            
            try:
                message = long_to_bytes(m_root).decode()
            except:
                message = str(long_to_bytes(m_root))
            
            steps.append(f"Bản rõ thu được: {message}")
            
            return {'success': True, 'message': message, 'steps': steps, 'recovered_m': str(m_root)}
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
    
    result = RSAService.encrypt_message(message, n, e)
    return jsonify(result)

@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    """API giải mã"""
    data = request.get_json()
    ciphertext = data.get('ciphertext', '')
    n = data.get('n', '')
    d = data.get('d', '')
    
    result = RSAService.decrypt_message(ciphertext, n, d)
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
    
    result = RSAService.hastad_attack(ciphertexts, public_keys)
    return jsonify(result)

@app.route('/api/generate_hastad_demo', methods=['POST'])
def api_generate_hastad_demo():
    """API tạo demo tấn công Håstad"""
    data = request.get_json()
    message = data.get('message', 'Hello')
    e = data.get('e', 3)
    bits = data.get('bits', 1024)
    count = data.get('count', 3)
    
    try:
        # Tạo nhiều cặp khóa
        keys = []
        ciphertexts = []
        
        for i in range(count):
            key_result = RSAService.generate_rsa_key(e=e, bits=bits)
            if not key_result['success']:
                return jsonify({'success': False, 'error': key_result['error']})
            
            # Mã hóa cùng một message
            encrypt_result = RSAService.encrypt_message(message, key_result['n'], key_result['e'])
            if not encrypt_result['success']:
                return jsonify({'success': False, 'error': encrypt_result['error']})
            
            keys.append({
                'n': key_result['n'],
                'e': key_result['e'],
                'd': key_result['d'],
                'index': i + 1
            })
            ciphertexts.append(encrypt_result['ciphertext'])
        
        return jsonify({
            'success': True,
            'message': message,
            'keys': keys,
            'ciphertexts': ciphertexts
        })
    except Exception as ex:
        return jsonify({'success': False, 'error': str(ex)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 