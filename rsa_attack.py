import sys
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
from sympy import mod_inverse, integer_nthroot

def generate_rsa_key(e=3, bits=1024):
    """Tạo cặp khóa RSA với số mũ công khai e"""
    while True:
        key = RSA.generate(bits, e=e)
        if key.e == e:
            return key

def encrypt_message(message, public_key):
    """Mã hóa tin nhắn với khóa công khai RSA"""
    message_int = bytes_to_long(message.encode())
    if message_int >= public_key.n:
        raise ValueError("Thông điệp quá dài so với modulus n.")
    return pow(message_int, public_key.e, public_key.n)

def decrypt_message(ciphertext, private_key):
    message_int = pow(ciphertext, private_key.d, private_key.n)
    try:
        return long_to_bytes(message_int).decode()
    except UnicodeDecodeError:
        return long_to_bytes(message_int)

def chinese_remainder_theorem(congruences, verbose=False):
    """Giải hệ phương trình đồng dư bằng định lý số dư Trung Hoa"""
    total = 0
    product = 1
    for _, mod in congruences:
        product *= mod
    if verbose:
        print(f"Tích các modulus (N): {product}")
    for i, (remainder, mod) in enumerate(congruences):
        p = product // mod
        inv = mod_inverse(p, mod)
        if verbose:
            print(f"Phần tử {i+1}: remainder={remainder}, mod={mod}, p={p}, inv={inv}")
        total += remainder * p * inv
    result = total % product
    if verbose:
        print(f"Kết quả CRT: {result}")
    return result

def low_exponent_attack_single(ciphertext, e, n, verbose=False):
    if verbose:
        print(f"Bản mã: {ciphertext}")
        print(f"Giải phương trình m^{e} = {ciphertext} (mod {n}) với m^e < n")
    m_root, exact = integer_nthroot(ciphertext, e)
    if verbose:
        print(f"Kết quả khai căn bậc {e}: {m_root}, chính xác: {exact}")
    if not exact:
        raise ValueError("Không tìm được căn bậc e chính xác. Có thể bản mã hoặc khóa không hợp lệ.")
    try:
        return long_to_bytes(m_root).decode()
    except UnicodeDecodeError:
        return long_to_bytes(m_root)

def low_exponent_attack_hastad(ciphertexts, public_keys, verbose=False):
    e = public_keys[0].e
    congruences = [(c, key.n) for c, key in zip(ciphertexts, public_keys)]
    result = chinese_remainder_theorem(congruences, verbose=verbose)
    m_root, exact = integer_nthroot(result, e)
    if verbose:
        print(f"Kết quả khai căn bậc {e}: {m_root}, chính xác: {exact}")
    if not exact:
        raise ValueError("Không tìm được căn bậc e chính xác. Có thể bản mã hoặc khóa không hợp lệ.")
    try:
        return long_to_bytes(m_root).decode()
    except UnicodeDecodeError:
        return long_to_bytes(m_root)

def menu():
    print("\n--- MENU ---")
    print("1. Sinh khóa RSA với tham số tùy chỉnh")
    print("2. Mã hóa bản rõ")
    print("3. Giải mã bản mã")
    print("4. Tấn công khai căn khi m^e < n")
    print("5. Tấn công Håstad (nhiều người nhận)")
    print("0. Thoát")
    return input("Chọn chức năng: ")

def main():
    keys = []
    last_cipher = None
    last_plain = None
    while True:
        choice = menu()
        if choice == '1':
            try:
                e = int(input("Nhập số mũ công khai e (ví dụ: 3): "))
                bits = int(input("Nhập số bit modulus (ví dụ: 1024): "))
                key = generate_rsa_key(e=e, bits=bits)
                keys.append(key)
                print(f"Khóa mới: n = {key.n}\ne = {key.e}\nd = {key.d}")
            except Exception as ex:
                print(f"Lỗi: {ex}")
        elif choice == '2':
            if not keys:
                print("Chưa có khóa nào. Hãy sinh khóa trước.")
                continue
            msg = input("Nhập bản rõ: ")
            try:
                pubkey = keys[-1]
                cipher = encrypt_message(msg, pubkey)
                last_cipher = cipher
                last_plain = msg
                print(f"Bản mã: {cipher}")
            except Exception as ex:
                print(f"Lỗi: {ex}")
        elif choice == '3':
            if not keys or last_cipher is None:
                print("Chưa có bản mã hoặc khóa.")
                continue
            try:
                privkey = keys[-1]
                plain = decrypt_message(last_cipher, privkey)
                print(f"Bản rõ giải mã: {plain}")
            except Exception as ex:
                print(f"Lỗi: {ex}")
        elif choice == '4':
            if not keys or last_cipher is None:
                print("Chưa có bản mã hoặc khóa.")
                continue
            try:
                pubkey = keys[-1]
                print("--- Quá trình tấn công khai căn ---")
                result = low_exponent_attack_single(last_cipher, pubkey.e, pubkey.n, verbose=True)
                print(f"Bản rõ thu được: {result}")
            except Exception as ex:
                print(f"Lỗi: {ex}")
        elif choice == '5':
            try:
                e = int(input("Nhập số mũ công khai e (ví dụ: 3): "))
                bits = int(input("Nhập số bit modulus (ví dụ: 1024): "))
                msg = input("Nhập bản rõ gửi cho nhiều người: ")
                k = e
                pubkeys = [generate_rsa_key(e=e, bits=bits) for _ in range(k)]
                ciphers = [encrypt_message(msg, pk) for pk in pubkeys]
                print("--- Thông tin các khóa công khai ---")
                for i, pk in enumerate(pubkeys):
                    print(f"Khóa {i+1}: n = {pk.n}")
                print("--- Các bản mã ---")
                for i, c in enumerate(ciphers):
                    print(f"Bản mã {i+1}: {c}")
                print("--- Quá trình tấn công Håstad ---")
                result = low_exponent_attack_hastad(ciphers, pubkeys, verbose=True)
                print(f"Bản rõ thu được: {result}")
            except Exception as ex:
                print(f"Lỗi: {ex}")
        elif choice == '0':
            print("Thoát.")
            break
        else:
            print("Lựa chọn không hợp lệ.")

if __name__ == "__main__":
    main()