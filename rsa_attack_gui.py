import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
from sympy import mod_inverse, integer_nthroot
import threading

class RSAAttackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RSA Low Exponent Attack Demo")
        self.root.geometry("800x600")
        
        # Biến lưu trữ
        self.keys = []
        self.last_cipher = None
        self.last_plain = None
        
        # Tạo notebook (tab)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Tab 1: Sinh khóa
        self.key_gen_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.key_gen_frame, text='Sinh khóa')
        self.setup_key_gen_tab()
        
        # Tab 2: Mã hóa/Giải mã
        self.crypto_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.crypto_frame, text='Mã hóa/Giải mã')
        self.setup_crypto_tab()
        
        # Tab 3: Tấn công
        self.attack_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.attack_frame, text='Tấn công')
        self.setup_attack_tab()
        
        # Tab 4: Lý thuyết
        self.theory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.theory_frame, text='Lý thuyết')
        self.setup_theory_tab()

    def setup_key_gen_tab(self):
        # Frame cho input
        input_frame = ttk.LabelFrame(self.key_gen_frame, text="Tham số sinh khóa")
        input_frame.pack(fill='x', padx=5, pady=5)
        
        # Số mũ e
        ttk.Label(input_frame, text="Số mũ công khai (e):").grid(row=0, column=0, padx=5, pady=5)
        self.e_var = tk.StringVar(value="3")
        ttk.Entry(input_frame, textvariable=self.e_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Số bit
        ttk.Label(input_frame, text="Số bit modulus:").grid(row=1, column=0, padx=5, pady=5)
        self.bits_var = tk.StringVar(value="1024")
        ttk.Entry(input_frame, textvariable=self.bits_var).grid(row=1, column=1, padx=5, pady=5)
        
        # Nút sinh khóa
        ttk.Button(input_frame, text="Sinh khóa", command=self.generate_key).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Kết quả
        result_frame = ttk.LabelFrame(self.key_gen_frame, text="Kết quả")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.key_result = scrolledtext.ScrolledText(result_frame, height=10)
        self.key_result.pack(fill='both', expand=True, padx=5, pady=5)

    def setup_crypto_tab(self):
        # Frame cho input
        input_frame = ttk.LabelFrame(self.crypto_frame, text="Mã hóa/Giải mã")
        input_frame.pack(fill='x', padx=5, pady=5)
        
        # Bản rõ
        ttk.Label(input_frame, text="Bản rõ:").grid(row=0, column=0, padx=5, pady=5)
        self.plain_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.plain_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Nút mã hóa
        ttk.Button(input_frame, text="Mã hóa", command=self.encrypt).grid(row=1, column=0, pady=5)
        
        # Nút giải mã
        ttk.Button(input_frame, text="Giải mã", command=self.decrypt).grid(row=1, column=1, pady=5)
        
        # Kết quả
        result_frame = ttk.LabelFrame(self.crypto_frame, text="Kết quả")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.crypto_result = scrolledtext.ScrolledText(result_frame, height=10)
        self.crypto_result.pack(fill='both', expand=True, padx=5, pady=5)

    def setup_attack_tab(self):
        # Frame cho tấn công
        attack_frame = ttk.LabelFrame(self.attack_frame, text="Tấn công")
        attack_frame.pack(fill='x', padx=5, pady=5)
        
        # Nút tấn công khai căn
        ttk.Button(attack_frame, text="Tấn công khai căn", 
                  command=self.single_attack).pack(fill='x', padx=5, pady=5)
        
        # Nút tấn công Håstad
        ttk.Button(attack_frame, text="Tấn công Håstad", 
                  command=self.hastad_attack).pack(fill='x', padx=5, pady=5)
        
        # Kết quả
        result_frame = ttk.LabelFrame(self.attack_frame, text="Kết quả tấn công")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.attack_result = scrolledtext.ScrolledText(result_frame, height=10)
        self.attack_result.pack(fill='both', expand=True, padx=5, pady=5)

    def setup_theory_tab(self):
        theory_text = """
RSA Low Exponent Attack Demo

1. Thuật toán RSA:
   - Sinh khóa:
     + Chọn hai số nguyên tố lớn p, q
     + Tính n = p × q, φ(n) = (p-1)(q-1)
     + Chọn số mũ công khai e sao cho 1 < e < φ(n) và gcd(e, φ(n)) = 1
     + Tính số mũ bí mật d sao cho e × d ≡ 1 (mod φ(n))
     + Khóa công khai: (n, e), Khóa bí mật: (n, d)
   
   - Mã hóa: c = m^e mod n
   - Giải mã: m = c^d mod n

2. Vai trò của số mũ công khai e:
   - e thường chọn là số lẻ nhỏ (3, 5, 17, 65537)
   - Nếu e quá nhỏ (3, 5), có thể bị tấn công

3. Các kiểu tấn công:
   - Tấn công khi m^e < n:
     + Nếu bản rõ nhỏ, c = m^e
     + Có thể khai căn bậc e để tìm lại m
   
   - Tấn công Håstad:
     + Khi cùng bản rõ gửi cho nhiều người với cùng e
     + Dùng định lý số dư Trung Hoa (CRT) để khôi phục
     + Cần ít nhất e bản mã khác nhau
"""
        theory_label = scrolledtext.ScrolledText(self.theory_frame, wrap=tk.WORD)
        theory_label.pack(fill='both', expand=True, padx=5, pady=5)
        theory_label.insert('1.0', theory_text)
        theory_label.config(state='disabled')

    def generate_key(self):
        try:
            e = int(self.e_var.get())
            bits = int(self.bits_var.get())
            
            def generate():
                key = RSA.generate(bits, e=e)
                if key.e == e:
                    self.keys.append(key)
                    result = f"Khóa mới:\nn = {key.n}\ne = {key.e}\nd = {key.d}"
                    self.key_result.delete('1.0', tk.END)
                    self.key_result.insert('1.0', result)
                else:
                    messagebox.showerror("Lỗi", "Không thể tạo khóa với e đã chọn")
            
            threading.Thread(target=generate).start()
            
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên hợp lệ")

    def encrypt(self):
        if not self.keys:
            messagebox.showerror("Lỗi", "Chưa có khóa nào. Hãy sinh khóa trước.")
            return
            
        try:
            msg = self.plain_var.get()
            pubkey = self.keys[-1]
            cipher = pow(bytes_to_long(msg.encode()), pubkey.e, pubkey.n)
            self.last_cipher = cipher
            self.last_plain = msg
            
            result = f"Bản mã: {cipher}"
            self.crypto_result.delete('1.0', tk.END)
            self.crypto_result.insert('1.0', result)
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def decrypt(self):
        if not self.keys or self.last_cipher is None:
            messagebox.showerror("Lỗi", "Chưa có bản mã hoặc khóa.")
            return
            
        try:
            privkey = self.keys[-1]
            plain = long_to_bytes(pow(self.last_cipher, privkey.d, privkey.n)).decode()
            
            result = f"Bản rõ giải mã: {plain}"
            self.crypto_result.delete('1.0', tk.END)
            self.crypto_result.insert('1.0', result)
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def single_attack(self):
        if not self.keys or self.last_cipher is None:
            messagebox.showerror("Lỗi", "Chưa có bản mã hoặc khóa.")
            return
            
        try:
            pubkey = self.keys[-1]
            result = []
            result.append("--- Quá trình tấn công khai căn ---")
            result.append(f"Bản mã: {self.last_cipher}")
            result.append(f"Giải phương trình m^{pubkey.e} = {self.last_cipher} (mod {pubkey.n})")
            
            m_root, exact = integer_nthroot(self.last_cipher, pubkey.e)
            result.append(f"Kết quả khai căn bậc {pubkey.e}: {m_root}")
            result.append(f"Căn chính xác: {exact}")
            
            if exact:
                try:
                    plain = long_to_bytes(m_root).decode()
                    result.append(f"Bản rõ thu được: {plain}")
                except UnicodeDecodeError:
                    result.append(f"Không thể giải mã kết quả: {m_root}")
            else:
                result.append("Không tìm được căn chính xác")
            
            self.attack_result.delete('1.0', tk.END)
            self.attack_result.insert('1.0', '\n'.join(result))
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def hastad_attack(self):
        try:
            e = int(self.e_var.get())
            bits = int(self.bits_var.get())
            msg = self.plain_var.get()
            
            if not msg:
                messagebox.showerror("Lỗi", "Vui lòng nhập bản rõ")
                return
            
            result = []
            result.append("--- Tấn công Håstad ---")
            
            # Tạo khóa và mã hóa
            pubkeys = [RSA.generate(bits, e=e) for _ in range(e)]
            ciphers = [pow(bytes_to_long(msg.encode()), pk.e, pk.n) for pk in pubkeys]
            
            result.append("Thông tin các khóa công khai:")
            for i, pk in enumerate(pubkeys):
                result.append(f"Khóa {i+1}: n = {pk.n}")
            
            result.append("\nCác bản mã:")
            for i, c in enumerate(ciphers):
                result.append(f"Bản mã {i+1}: {c}")
            
            # Thực hiện tấn công
            result.append("\n--- Quá trình tấn công ---")
            
            # Áp dụng CRT
            congruences = [(c, key.n) for c, key in zip(ciphers, pubkeys)]
            crt_result = self.chinese_remainder_theorem(congruences)
            result.append(f"Kết quả CRT: {crt_result}")
            
            # Khai căn
            m_root, exact = integer_nthroot(crt_result, e)
            result.append(f"Kết quả khai căn bậc {e}: {m_root}")
            result.append(f"Căn chính xác: {exact}")
            
            if exact:
                try:
                    plain = long_to_bytes(m_root).decode()
                    result.append(f"Bản rõ thu được: {plain}")
                except UnicodeDecodeError:
                    result.append(f"Không thể giải mã kết quả: {m_root}")
            else:
                result.append("Không tìm được căn chính xác")
            
            self.attack_result.delete('1.0', tk.END)
            self.attack_result.insert('1.0', '\n'.join(result))
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def chinese_remainder_theorem(self, congruences):
        total = 0
        product = 1
        for _, mod in congruences:
            product *= mod
        for remainder, mod in congruences:
            p = product // mod
            total += remainder * p * mod_inverse(p, mod)
        return total % product

if __name__ == "__main__":
    root = tk.Tk()
    app = RSAAttackGUI(root)
    root.mainloop() 