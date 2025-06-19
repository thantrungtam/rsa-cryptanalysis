// Hàm utility
function formatNumber(num) {
    // Trả về số nguyên đầy đủ không có dấu phẩy
    if (!num || num === 'N/A') return num;

    let numStr = '';
    if (typeof num === 'string') {
        numStr = num.replace(/,/g, ''); // Loại bỏ dấu phẩy nếu có
    } else {
        numStr = String(num).replace(/,/g, ''); // Chuyển thành string và loại bỏ dấu phẩy
    }

    return numStr;
}

function formatNumberForDisplay(num, maxLength = 80) {
    // Format số cho hiển thị trong step, rút gọn nếu quá dài, loại bỏ dấu phẩy
    let numStr = '';
    if (typeof num === 'string') {
        numStr = num.replace(/,/g, ''); // Loại bỏ dấu phẩy
    } else {
        numStr = String(num).replace(/,/g, ''); // Loại bỏ dấu phẩy
    }

    if (numStr.length > maxLength) {
        const truncated = numStr.substring(0, 50) + '\n...\n' + numStr.substring(numStr.length - 30);
        return truncated + '\n[' + numStr.length + ' chữ số]';
    }
    return numStr;
}

// Removed expandable number functions - now using simple textarea display

function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'block';
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}

function showResult(containerId, content, type = 'info') {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = content;
    container.className = `result-section result-${type}`;
    container.style.display = 'block';
}

function clearResult(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.style.display = 'none';
        container.innerHTML = '';
    }
}

// Tab management
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// RSA Key Generation
async function generateRSAKey() {
    const e = parseInt(document.getElementById('exponent').value) || 3;
    const bits = parseInt(document.getElementById('key-bits').value) || 1024;

    showLoading('key-loading');
    clearResult('key-result');

    try {
        const response = await fetch('/api/generate_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ e: e, bits: bits })
        });

        const result = await response.json();
        hideLoading('key-loading');

        if (result.success) {
            const keyHTML = `
                <h3>🔑 Cặp khóa RSA đã được tạo thành công!</h3>
                
                <div class="steps-container">
                    <h4>📋 Các bước sinh khóa RSA:</h4>
                    <div class="step-item">
                        <span class="step-number">Bước 1:</span>
                        <span class="step-math">Chọn hai số nguyên tố lớn p và q</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 2:</span>
                        <span class="step-math">Tính modulus: n = p × q = ${formatNumberForDisplay(result.p)} × ${formatNumberForDisplay(result.q)} = ${formatNumberForDisplay(result.n)}</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 3:</span>
                        <span class="step-math">Tính hàm Euler: φ(n) = (p-1) × (q-1) = ${formatNumberForDisplay(result.p - 1)} × ${formatNumberForDisplay(result.q - 1)}</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 4:</span>
                        <span class="step-math">Chọn số mũ công khai e = ${result.e} (gcd(e, φ(n)) = 1)</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 5:</span>
                        <span class="step-math">Tính số mũ riêng d sao cho e × d ≡ 1 (mod φ(n))</span>
                    </div>
                </div>

                <div class="key-display">
                    <h4>🔐 Thông tin khóa chi tiết:</h4>
                    <div class="key-row">
                        <span class="key-label">Số nguyên tố p:</span>
                        <textarea class="key-textarea" readonly>${formatNumber(result.p)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Số nguyên tố q:</span>
                        <textarea class="key-textarea" readonly>${formatNumber(result.q)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Modulus (n = p×q):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(result.n)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Số mũ công khai (e):</span>
                        <span class="key-value short">${result.e}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Số mũ riêng (d):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(result.d)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Độ dài khóa:</span>
                        <span class="key-value short">${result.bits} bits</span>
                    </div>
                </div>
                
                <div class="warning-box mt-2">
                    <strong>⚠️ Cảnh báo bảo mật:</strong> Với e = ${result.e}, khóa này dễ bị tấn công nếu bản rõ nhỏ (m^e < n)!
                </div>
            `;
            showResult('key-result', keyHTML, 'success');

            // Lưu khóa vào form
            document.getElementById('encrypt-n').value = result.n;
            document.getElementById('encrypt-e').value = result.e;
            document.getElementById('decrypt-n').value = result.n;
            document.getElementById('decrypt-d').value = result.d;
            document.getElementById('attack-n').value = result.n;
            document.getElementById('attack-e').value = result.e;
        } else {
            showResult('key-result', `<h3>❌ Lỗi tạo khóa</h3><p>${result.error}</p>`, 'error');
        }
    } catch (error) {
        hideLoading('key-loading');
        showResult('key-result', `<h3>❌ Lỗi kết nối</h3><p>${error.message}</p>`, 'error');
    }
}

// RSA Encryption
async function encryptMessage() {
    const message = document.getElementById('encrypt-message').value;
    const n = document.getElementById('encrypt-n').value;
    const e = document.getElementById('encrypt-e').value;
    const paddingType = document.getElementById('encrypt-padding').value;
    const inputType = 'text'; // Chỉ sử dụng text

    if (!message || !n || !e) {
        showResult('encrypt-result', '<h3>⚠️ Thiếu thông tin</h3><p>Vui lòng nhập đầy đủ thông tin!</p>', 'warning');
        return;
    }

    showLoading('encrypt-loading');
    clearResult('encrypt-result');

    try {
        const response = await fetch('/api/encrypt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                n: n,
                e: e,
                input_type: inputType,
                padding_type: paddingType
            })
        });

        const result = await response.json();
        hideLoading('encrypt-loading');

        if (result.success) {
            const encryptHTML = `
                <h3>🔒 Mã hóa RSA thành công!</h3>
                
                <div class="steps-container">
                    <h4>📋 Các bước mã hóa RSA:</h4>
                    <div class="step-item">
                        <span class="step-number">Bước 1:</span>
                        <span class="step-math">Chuyển đổi văn bản thành số: "${result.original_display}" → ${formatNumberForDisplay(result.message_int)}</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 2:</span>
                        <span class="step-math">Áp dụng công thức mã hóa: c ≡ m^e (mod n)</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 3:</span>
                        <span class="step-math">Tính toán: c ≡ ${formatNumberForDisplay(result.message_int)}^${e} (mod ${formatNumberForDisplay(n)})</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 4:</span>
                        <span class="step-math">Kết quả: c = ${formatNumberForDisplay(result.ciphertext)}</span>
                    </div>
                </div>

                <div class="key-display">
                    <h4>📊 Thông tin mã hóa:</h4>
                    <div class="key-row">
                        <span class="key-label">Văn bản gốc:</span>
                        <span class="key-value">"${result.original_display}"</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Loại padding:</span>
                        <span class="key-value">${result.padding_info}</span>
                    </div>
                    ${result.message_int !== 'N/A (sử dụng padding)' ? `
                    <div class="key-row">
                        <span class="key-label">Giá trị số nguyên (m):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(result.message_int)}</textarea>
                    </div>
                    ` : ''}
                    <div class="key-row">
                        <span class="key-label">Số mũ công khai (e):</span>
                        <span class="key-value short">${e}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Modulus (n):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(n)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Bản mã (c):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(result.ciphertext)}</textarea>
                    </div>
                </div>
                
                <div class="step-item mt-2">
                    <span class="step-number">🔍 Phân tích bảo mật:</span> 
                    <span class="step-math">${result.comparison.replace(/,/g, '')}</span>
                </div>
                
                ${result.is_vulnerable ?
                    '<div class="warning-box mt-2"><strong>⚠️ NGUY HIỂM:</strong> m^e < n, bản mã có thể bị tấn công khai căn! Kẻ tấn công có thể tính m = ∛c để khôi phục bản rõ.</div>' :
                    '<div class="attack-example mt-2"><strong>✅ AN TOÀN:</strong> m^e ≥ n, không thể tấn công khai căn trực tiếp vì phép modulo đã có tác dụng.</div>'
                }
            `;
            showResult('encrypt-result', encryptHTML, 'success');

            // Lưu bản mã để giải mã hoặc tấn công
            document.getElementById('decrypt-ciphertext').value = result.ciphertext;
            document.getElementById('attack-ciphertext').value = result.ciphertext;
        } else {
            showResult('encrypt-result', `<h3>❌ Lỗi mã hóa</h3><p>${result.error}</p>`, 'error');
        }
    } catch (error) {
        hideLoading('encrypt-loading');
        showResult('encrypt-result', `<h3>❌ Lỗi kết nối</h3><p>${error.message}</p>`, 'error');
    }
}

// RSA Decryption
async function decryptMessage() {
    const ciphertext = document.getElementById('decrypt-ciphertext').value;
    const n = document.getElementById('decrypt-n').value;
    const d = document.getElementById('decrypt-d').value;
    const e = document.getElementById('encrypt-e').value; // Lấy e từ encrypt tab
    const paddingType = document.getElementById('decrypt-padding').value;

    if (!ciphertext || !n || !d) {
        showResult('decrypt-result', '<h3>⚠️ Thiếu thông tin</h3><p>Vui lòng nhập đầy đủ thông tin!</p>', 'warning');
        return;
    }

    showLoading('decrypt-loading');
    clearResult('decrypt-result');

    try {
        const response = await fetch('/api/decrypt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ciphertext: ciphertext,
                n: n,
                d: d,
                e: e,
                padding_type: paddingType
            })
        });

        const result = await response.json();
        hideLoading('decrypt-loading');

        if (result.success) {
            const decryptHTML = `
                <h3>🔓 Giải mã RSA thành công!</h3>
                
                <div class="steps-container">
                    <h4>📋 Các bước giải mã RSA:</h4>
                    <div class="step-item">
                        <span class="step-number">Bước 1:</span>
                        <span class="step-math">Áp dụng công thức giải mã: m ≡ c^d (mod n)</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 2:</span>
                        <span class="step-math">Tính toán: m ≡ ${formatNumberForDisplay(ciphertext)}^${formatNumberForDisplay(d)} (mod ${formatNumberForDisplay(n)})</span>
                    </div>
                    ${result.message_int !== 'N/A' ? `
                    <div class="step-item">
                        <span class="step-number">Bước 3:</span>
                        <span class="step-math">Kết quả số nguyên: m = ${formatNumberForDisplay(result.message_int)}</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 4:</span>
                        <span class="step-math">Chuyển đổi về văn bản: ${formatNumberForDisplay(result.message_int)} → "${result.message}"</span>
                    </div>
                    ` : `
                    <div class="step-item">
                        <span class="step-number">Bước 3:</span>
                        <span class="step-math">Giải mã bằng padding scheme: ${result.padding_type}</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 4:</span>
                        <span class="step-math">Kết quả: "${result.message}"</span>
                    </div>
                    `}
                </div>

                <div class="key-display">
                    <h4>📊 Thông tin giải mã:</h4>
                    <div class="key-row">
                        <span class="key-label">Bản mã (c):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(ciphertext)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Loại padding:</span>
                        <span class="key-value">${result.padding_type}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Số mũ riêng (d):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(d)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Modulus (n):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(n)}</textarea>
                    </div>
                    ${result.message_int !== 'N/A' ? `
                    <div class="key-row">
                        <span class="key-label">Bản rõ (số nguyên):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(result.message_int)}</textarea>
                    </div>
                    ` : ''}
                    <div class="key-row">
                        <span class="key-label">Bản rõ (văn bản):</span>
                        <span class="key-value">"${result.message}"</span>
                    </div>
                </div>
                
                <div class="attack-example mt-2">
                    <strong>✅ Thành công:</strong> Giải mã RSA hoàn tất với khóa riêng hợp lệ!
                </div>
            `;
            showResult('decrypt-result', decryptHTML, 'success');
        } else {
            showResult('decrypt-result', `<h3>❌ Lỗi giải mã</h3><p>${result.error}</p>`, 'error');
        }
    } catch (error) {
        hideLoading('decrypt-loading');
        showResult('decrypt-result', `<h3>❌ Lỗi kết nối</h3><p>${error.message}</p>`, 'error');
    }
}

// Single Attack (Cube Root Attack)
async function performSingleAttack() {
    const ciphertext = document.getElementById('attack-ciphertext').value;
    const n = document.getElementById('attack-n').value;
    const e = document.getElementById('attack-e').value;

    if (!ciphertext || !n || !e) {
        showResult('attack-result', '<h3>⚠️ Thiếu thông tin</h3><p>Vui lòng nhập đầy đủ thông tin!</p>', 'warning');
        return;
    }

    showLoading('attack-loading');
    clearResult('attack-result');

    try {
        const response = await fetch('/api/attack_single', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ciphertext: ciphertext, n: n, e: e })
        });

        const result = await response.json();
        hideLoading('attack-loading');

        if (result.success) {
            const attackHTML = `
                <h3>🎯 Tấn công khai căn thành công!</h3>
                
                <div class="steps-container">
                    <h4>🕵️ Các bước tấn công khai căn:</h4>
                    <div class="step-item">
                        <span class="step-number">Bước 1:</span>
                        <span class="step-math">Kiểm tra điều kiện: m^e < n (bản rõ nhỏ)</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 2:</span>
                        <span class="step-math">Vì m^e < n nên c = m^e (không có modulo thực sự)</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 3:</span>
                        <span class="step-math">Tính căn bậc ${result.e || 'e'}: m = ∛c = ∛${formatNumberForDisplay(result.ciphertext || 'c')} = ${formatNumberForDisplay(result.recovered_m)}</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 4:</span>
                        <span class="step-math">Kết quả: m = ${formatNumberForDisplay(result.recovered_m)}</span>
                    </div>
                    <div class="step-item">
                        <span class="step-number">Bước 5:</span>
                        <span class="step-math">Chuyển đổi về văn bản: ${formatNumberForDisplay(result.recovered_m)} → "${result.message}"</span>
                    </div>
                </div>

                <div class="key-display">
                    <h4>📊 Kết quả tấn công:</h4>
                    <div class="key-row">
                        <span class="key-label">Bản mã bị tấn công (c):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(result.ciphertext || ciphertext)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Modulus (n):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(n)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Số mũ công khai (e):</span>
                        <span class="key-value short">${result.e || e}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Bản rõ khôi phục (m):</span>
                        <textarea class="key-textarea" readonly>${formatNumber(result.recovered_m)}</textarea>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Văn bản khôi phục:</span>
                        <span class="key-value">"${result.message}"</span>
                    </div>
                </div>
                
                <div class="warning-box mt-2">
                    <strong>🚨 Kết luận:</strong> RSA với số mũ nhỏ (e=${result.e || e}) và bản rõ nhỏ có thể bị phá dễ dàng bằng tấn công khai căn!
                </div>
                
                <div class="attack-example mt-2">
                    <strong>💡 Cách phòng chống:</strong> Sử dụng padding (OAEP), số mũ lớn hơn (e=65537), hoặc đảm bảo m^e ≥ n.
                </div>
            `;
            showResult('attack-result', attackHTML, 'success');
        } else {
            const errorHTML = `
                <h3>❌ Tấn công thất bại</h3>
                <p>${result.error}</p>
                ${result.steps ? `
                    <div class="steps-container">
                        <h4>Các bước đã thực hiện:</h4>
                        ${result.steps.map((step, index) => `<div class="step-item"><span class="step-number">Bước ${index + 1}:</span><span class="step-math">${step}</span></div>`).join('')}
                    </div>
                ` : ''}
                <div class="attack-example mt-2">
                    <strong>💡 Lý do:</strong> Có thể bản rõ quá lớn (m^e ≥ n) hoặc dữ liệu không hợp lệ.
                </div>
            `;
            showResult('attack-result', errorHTML, 'error');
        }
    } catch (error) {
        hideLoading('attack-loading');
        showResult('attack-result', `<h3>❌ Lỗi kết nối</h3><p>${error.message}</p>`, 'error');
    }
}

// Generate Håstad Demo
async function generateHastadDemo() {
    const message = document.getElementById('hastad-message').value || 'Hello';
    const e = parseInt(document.getElementById('hastad-e').value) || 3;
    const bits = parseInt(document.getElementById('hastad-bits').value) || 1024;
    const count = parseInt(document.getElementById('hastad-count').value) || 3;
    const paddingType = document.getElementById('hastad-padding').value;
    const inputType = 'text'; // Chỉ sử dụng text

    showLoading('hastad-demo-loading');
    clearResult('hastad-demo-result');

    try {
        const response = await fetch('/api/generate_hastad_demo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                e: e,
                bits: bits,
                count: count,
                input_type: inputType,
                padding_type: paddingType
            })
        });

        const result = await response.json();
        hideLoading('hastad-demo-loading');

        if (result.success) {
            // Hiển thị các khóa công khai với grid layout
            let keysHTML = `
                <div class="hastad-section">
                    <h4>🔑 Các khóa công khai</h4>
                    <div class="hastad-keys-grid">
            `;
            result.keys.forEach((key, index) => {
                keysHTML += `
                    <div class="hastad-key-item">
                        <div class="key-title">Khóa ${key.index}</div>
                        <div class="key-row">
                            <span class="key-label">n${key.index} =</span>
                            <textarea class="key-textarea" readonly>${formatNumber(key.n)}</textarea>
                        </div>
                        <div class="key-row">
                            <span class="key-label">e${key.index} =</span>
                            <span class="key-value">${key.e}</span>
                        </div>
                    </div>
                `;
            });
            keysHTML += `
                    </div>
                </div>
            `;

            // Hiển thị các bản mã với list layout
            let ciphersHTML = `
                <div class="hastad-section">
                    <h4>🔒 Các bản mã tương ứng</h4>
                    <div class="hastad-ciphers-list">
            `;
            result.ciphertexts.forEach((cipher, index) => {
                ciphersHTML += `
                    <div class="hastad-cipher-item">
                        <div class="hastad-cipher-index">${index + 1}</div>
                        <div class="key-row" style="flex: 1;">
                            <span class="key-label">c${index + 1} =</span>
                            <textarea class="key-textarea" readonly>${formatNumber(cipher)}</textarea>
                        </div>
                    </div>
                `;
            });
            ciphersHTML += `
                    </div>
                </div>
            `;

            const inputTypeDisplay = result.input_type === 'integer' ? 'Số nguyên' : 'Văn bản';
            const messageDisplay = result.input_type === 'integer' ? result.message : `"${result.message}"`;

            // Hiển thị phân tích tấn công
            let attackAnalysisHTML = '';
            if (result.attack_analysis) {
                const analysis = result.attack_analysis;
                attackAnalysisHTML = `
                    <div class="warning-box" style="border-left: 4px solid ${analysis.can_attack ? '#ff4444' : '#00aa44'};">
                        <h4>🎯 Phân tích khả năng tấn công:</h4>
                        <div class="key-row">
                            <span class="key-label">Trạng thái:</span>
                            <span class="key-value" style="color: ${analysis.can_attack ? '#ff4444' : '#00aa44'}; font-weight: bold;">
                                ${analysis.can_attack ? '⚠️ CÓ THỂ BỊ TẤN CÔNG' : '🛡️ ĐƯỢC BẢO VỆ'}
                            </span>
                        </div>
                        <div class="key-row">
                            <span class="key-label">Lý do:</span>
                            <span class="key-value">${analysis.reason}</span>
                        </div>
                        <div class="key-row">
                            <span class="key-label">Cơ chế bảo vệ:</span>
                            <span class="key-value">${analysis.padding_effectiveness}</span>
                        </div>
                        <p><strong>📚 Giáo dục:</strong> ${analysis.educational_note}</p>
                    </div>
                `;
            }

            const demoHTML = `
                <h3>📋 Demo Tấn công Håstad đã sẵn sàng!</h3>
                <div class="key-display">
                    <div class="key-row">
                        <span class="key-label">Bản rõ gốc:</span>
                        <span class="key-value">${messageDisplay}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Kiểu dữ liệu:</span>
                        <span class="key-value">${inputTypeDisplay}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Số mũ công khai (e):</span>
                        <span class="key-value">${e}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Số lượng khóa:</span>
                        <span class="key-value">${count}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Loại padding:</span>
                        <span class="key-value">${result.padding_type}</span>
                    </div>
                </div>
                ${attackAnalysisHTML}
                ${keysHTML}
                ${ciphersHTML}
                <div class="attack-example mt-2">
                    <strong>📝 Thử nghiệm:</strong> Cùng một bản rõ "${result.message}" được mã hóa với ${count} khóa khác nhau có cùng e=${e}. 
                    ${result.attack_analysis?.can_attack ?
                    'Bây giờ hãy thực hiện tấn công Håstad bên dưới để xem nó hoạt động!' :
                    'Hãy thử tấn công bên dưới để xem padding bảo vệ như thế nào!'
                }
                </div>
            `;
            showResult('hastad-demo-result', demoHTML, 'success');

            // Điền dữ liệu vào form tấn công
            const ciphertextArea = document.getElementById('hastad-ciphertexts');
            const keysArea = document.getElementById('hastad-keys');

            ciphertextArea.value = result.ciphertexts.join('\n');

            let keysText = '';
            result.keys.forEach(key => {
                keysText += `${key.n},${key.e}\n`;
            });
            keysArea.value = keysText.trim();

            // Lưu thông tin để tấn công (global variables hoặc data attributes)
            window.hastadDemoData = {
                padding_type: result.padding_type,
                original_message: result.message,
                attack_analysis: result.attack_analysis
            };

        } else {
            showResult('hastad-demo-result', `<h3>❌ Lỗi tạo demo</h3><p>${result.error}</p>`, 'error');
        }
    } catch (error) {
        hideLoading('hastad-demo-loading');
        showResult('hastad-demo-result', `<h3>❌ Lỗi kết nối</h3><p>${error.message}</p>`, 'error');
    }
}

// Håstad Attack
async function performHastadAttack() {
    const ciphertextsText = document.getElementById('hastad-ciphertexts').value;
    const keysText = document.getElementById('hastad-keys').value;

    if (!ciphertextsText || !keysText) {
        showResult('hastad-attack-result', '<h3>⚠️ Thiếu thông tin</h3><p>Vui lòng nhập các bản mã và khóa công khai!</p>', 'warning');
        return;
    }

    // Parse input
    const ciphertexts = ciphertextsText.split('\n').filter(line => line.trim());
    const keyLines = keysText.split('\n').filter(line => line.trim());

    if (ciphertexts.length !== keyLines.length) {
        showResult('hastad-attack-result', '<h3>⚠️ Dữ liệu không khớp</h3><p>Số lượng bản mã và khóa phải bằng nhau!</p>', 'warning');
        return;
    }

    const publicKeys = keyLines.map(line => {
        const [n, e] = line.split(',');
        return { n: n.trim(), e: e.trim() };
    });

    showLoading('hastad-attack-loading');
    clearResult('hastad-attack-result');

    try {
        // Lấy thông tin padding từ demo data nếu có
        const demoData = window.hastadDemoData || {};
        const paddingType = demoData.padding_type || 'raw';
        const originalMessage = demoData.original_message || null;

        const response = await fetch('/api/attack_hastad', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ciphertexts: ciphertexts,
                public_keys: publicKeys,
                padding_type: paddingType,
                original_message: originalMessage
            })
        });

        const result = await response.json();
        hideLoading('hastad-attack-loading');

        if (result.success) {
            // Hiển thị thông tin về padding
            const displayPaddingType = paddingType || 'raw';
            const paddingInfo = displayPaddingType === 'raw' ?
                'Raw RSA (không có padding)' :
                `Padding ${displayPaddingType} (đã được bỏ qua do tấn công thành công)`;

            const attackHTML = `
                <h3>🎯 Tấn công Håstad thành công!</h3>
                
                ${result.steps ? `
                    <div class="steps-container">
                        <h4>🔍 Chi tiết quá trình tấn công:</h4>
                        ${result.steps.map((step, index) =>
                `<div class="step-item">
                                <span class="step-number">${index + 1}</span>
                                <span class="step-math">${step}</span>
                            </div>`
            ).join('')}
                    </div>
                ` : ''}

                <div class="key-display">
                    <h4>📊 Kết quả tấn công Håstad:</h4>
                    <div class="key-row">
                        <span class="key-label">Số lượng bản mã:</span>
                        <span class="key-value short">${ciphertexts.length}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Số mũ công khai (e):</span>
                        <span class="key-value short">${publicKeys[0]?.e}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Loại padding:</span>
                        <span class="key-value">${paddingInfo}</span>
                    </div>
                    <div class="key-row">
                        <span class="key-label">Bản rõ khôi phục:</span>
                        <span class="key-value">"${result.message}"</span>
                    </div>
                    ${originalMessage ? `
                    <div class="key-row">
                        <span class="key-label">So sánh gốc:</span>
                        <span class="key-value" style="color: ${result.message === originalMessage ? '#00aa44' : '#ff4444'};">
                            ${result.message === originalMessage ? '✅ Khớp hoàn toàn!' : '❌ Khác với bản gốc'}
                        </span>
                    </div>
                    ` : ''}
                </div>
                
                <div class="warning-box mt-2" style="border-left: 4px solid #ff4444;">
                    <strong>🚨 Kết luận:</strong> Tấn công Håstad thành công! 
                    ${displayPaddingType === 'raw' ?
                    'Raw RSA hoàn toàn không an toàn khi gửi cùng bản rõ với cùng e nhỏ!' :
                    `Mặc dù sử dụng padding ${displayPaddingType}, tấn công vẫn thành công (điều này bất thường và cần điều tra thêm).`
                }
                </div>
                
                <div class="attack-example mt-2">
                    <strong>💡 Cách phòng chống:</strong> 
                    <ul>
                        <li>Sử dụng padding ngẫu nhiên (PKCS#1 v1.5, OAEP)</li>
                        <li>Tránh gửi cùng bản rõ tới nhiều người</li>
                        <li>Sử dụng e lớn hơn (65537)</li>
                        <li>Thêm salt ngẫu nhiên vào message</li>
                    </ul>
                </div>
            `;
            showResult('hastad-attack-result', attackHTML, 'success');
        } else {
            // Xử lý trường hợp thất bại với thông tin chi tiết về padding
            const demoData = window.hastadDemoData || {};
            const failPaddingType = demoData.padding_type || 'raw';

            let errorHTML = '';

            if (result.padding_protected) {
                // Trường hợp padding chống được tấn công
                errorHTML = `
                    <h3>🛡️ Tấn công bị chặn bởi Padding!</h3>
                    
                    <div class="warning-box" style="border-left: 4px solid #00aa44;">
                        <h4>✅ Kết quả: Padding ${failPaddingType} đã bảo vệ thành công!</h4>
                        <p><strong>Lý do:</strong> ${result.error}</p>
                    </div>
                    
                    ${result.steps ? `
                        <div class="steps-container">
                            <h4>🔍 Chi tiết quá trình tấn công:</h4>
                            ${result.steps.map((step, index) =>
                    `<div class="step-item">
                                    <span class="step-number">${index + 1}</span>
                                    <span class="step-math">${step}</span>
                                </div>`
                ).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="key-display">
                        <h4>📊 Thông tin tấn công:</h4>
                        <div class="key-row">
                            <span class="key-label">Loại padding:</span>
                            <span class="key-value">${failPaddingType}</span>
                        </div>
                        <div class="key-row">
                            <span class="key-label">Trạng thái bảo mật:</span>
                            <span class="key-value" style="color: #00aa44; font-weight: bold;">🛡️ ĐƯỢC BẢO VỆ</span>
                        </div>
                        ${result.raw_recovered ? `
                        <div class="key-row">
                            <span class="key-label">Dữ liệu thô thu được:</span>
                            <textarea class="key-textarea" readonly>${result.raw_recovered}</textarea>
                        </div>
                        ` : ''}
                    </div>
                    
                    <div class="attack-example mt-2" style="border-left: 4px solid #00aa44;">
                        <h4>🔒 Tại sao padding chống được tấn công Håstad?</h4>
                        <ul>
                            <li><strong>PKCS#1 v1.5:</strong> Thêm random padding, làm mỗi lần mã hóa tạo ra kết quả khác nhau</li>
                            <li><strong>OAEP:</strong> Sử dụng hash và random padding, đảm bảo tính ngẫu nhiên cao</li>
                            <li><strong>Kết quả:</strong> Không còn cùng message được mã hóa thành cùng pattern</li>
                            <li><strong>Chinese Remainder Theorem:</strong> Không áp dụng được do dữ liệu khác nhau</li>
                        </ul>
                    </div>
                    
                    <div class="warning-box mt-2">
                        <strong>🎓 Bài học:</strong> Đây chính là lý do tại sao KHÔNG BAO GIỜ sử dụng Raw RSA trong thực tế. 
                        Padding schemes đã được thiết kế để chống lại chính xác loại tấn công này!
                    </div>
                `;
            } else {
                // Trường hợp lỗi khác
                errorHTML = `
                    <h3>❌ Tấn công thất bại</h3>
                    <div class="warning-box" style="border-left: 4px solid #ff4444;">
                        <p><strong>Lỗi:</strong> ${result.error}</p>
                        <p><strong>Loại padding:</strong> ${failPaddingType}</p>
                    </div>
                    
                    ${result.steps ? `
                        <div class="steps-container">
                            <h4>🔍 Các bước đã thực hiện:</h4>
                            ${result.steps.map((step, index) =>
                    `<div class="step-item">
                                    <span class="step-number">${index + 1}</span>
                                    <span class="step-math">${step}</span>
                                </div>`
                ).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="attack-example mt-2">
                        <strong>💡 Khuyến nghị:</strong> 
                        <ul>
                            <li>Kiểm tra dữ liệu đầu vào (bản mã và khóa)</li>
                            <li>Đảm bảo cùng bản rõ được mã hóa với các khóa khác nhau</li>
                            <li>Thử với Raw RSA để xem tấn công cơ bản</li>
                        </ul>
                    </div>
                `;
            }

            showResult('hastad-attack-result', errorHTML, result.padding_protected ? 'success' : 'error');
        }
    } catch (error) {
        hideLoading('hastad-attack-loading');
        showResult('hastad-attack-result', `<h3>❌ Lỗi kết nối</h3><p>${error.message}</p>`, 'error');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {

    initializeTabs();

    // Set default active tab
    const firstTab = document.querySelector('.tab-button');
    if (firstTab) {
        firstTab.click();
    }

    // Add event listeners for buttons
    const generateKeyBtn = document.getElementById('generate-key-btn');
    if (generateKeyBtn) {
        generateKeyBtn.addEventListener('click', generateRSAKey);
    }

    const encryptBtn = document.getElementById('encrypt-btn');
    if (encryptBtn) {
        encryptBtn.addEventListener('click', encryptMessage);
    }

    const decryptBtn = document.getElementById('decrypt-btn');
    if (decryptBtn) {
        decryptBtn.addEventListener('click', decryptMessage);
    }

    const attackBtn = document.getElementById('attack-btn');
    if (attackBtn) {
        attackBtn.addEventListener('click', performSingleAttack);
    }

    const hastadDemoBtn = document.getElementById('hastad-demo-btn');
    if (hastadDemoBtn) {
        hastadDemoBtn.addEventListener('click', generateHastadDemo);
    }

    const hastadAttackBtn = document.getElementById('hastad-attack-btn');
    if (hastadAttackBtn) {
        hastadAttackBtn.addEventListener('click', performHastadAttack);
    }

}); 