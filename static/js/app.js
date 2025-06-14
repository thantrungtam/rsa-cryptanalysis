// Hàm utility
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
                <div class="key-display">
                    <strong>Số mũ công khai (e):</strong> ${result.e}<br>
                    <strong>Modulus (n):</strong> ${result.n}<br>
                    <strong>Số mũ riêng (d):</strong> ${result.d}<br>
                    <strong>Số nguyên tố p:</strong> ${result.p}<br>
                    <strong>Số nguyên tố q:</strong> ${result.q}<br>
                    <strong>Độ dài khóa:</strong> ${result.bits} bits
                </div>
                <div class="warning-box mt-2">
                    <strong>⚠️ Cảnh báo:</strong> Với e = ${result.e}, khóa này dễ bị tấn công nếu bản rõ nhỏ!
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
            body: JSON.stringify({ message: message, n: n, e: e })
        });

        const result = await response.json();
        hideLoading('encrypt-loading');

        if (result.success) {
            const encryptHTML = `
                <h3>🔒 Mã hóa thành công!</h3>
                <div class="key-display">
                    <strong>Bản rõ:</strong> "${message}"<br>
                    <strong>Bản rõ (số nguyên):</strong> ${result.message_int}<br>
                    <strong>Bản mã:</strong> ${result.ciphertext}
                </div>
                <div class="step-item">
                    <strong>Phân tích:</strong> ${result.comparison}
                </div>
                ${parseInt(result.message_int) ** parseInt(e) < parseInt(n) ?
                    '<div class="warning-box mt-2"><strong>⚠️ Nguy hiểm:</strong> m^e < n, có thể bị tấn công khai căn!</div>' :
                    '<div class="attack-example mt-2"><strong>✅ An toàn:</strong> m^e ≥ n, không thể tấn công khai căn trực tiếp.</div>'
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
            body: JSON.stringify({ ciphertext: ciphertext, n: n, d: d })
        });

        const result = await response.json();
        hideLoading('decrypt-loading');

        if (result.success) {
            const decryptHTML = `
                <h3>🔓 Giải mã thành công!</h3>
                <div class="key-display">
                    <strong>Bản mã:</strong> ${ciphertext}<br>
                    <strong>Bản rõ (số nguyên):</strong> ${result.message_int}<br>
                    <strong>Bản rõ:</strong> "${result.message}"
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
            let stepsHTML = '<div class="steps-container"><h4>🕵️ Các bước tấn công:</h4>';
            result.steps.forEach((step, index) => {
                stepsHTML += `<div class="step-item"><span class="step-number">Bước ${index + 1}:</span> ${step}</div>`;
            });
            stepsHTML += '</div>';

            const attackHTML = `
                <h3>🎯 Tấn công khai căn thành công!</h3>
                <div class="key-display">
                    <strong>Bản rõ đã khôi phục:</strong> "${result.message}"<br>
                    <strong>Giá trị số nguyên:</strong> ${result.recovered_m}
                </div>
                ${stepsHTML}
                <div class="warning-box mt-2">
                    <strong>🔓 Kết luận:</strong> RSA với e nhỏ và bản rõ nhỏ có thể bị phá dễ dàng!
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
                        ${result.steps.map((step, index) => `<div class="step-item"><span class="step-number">Bước ${index + 1}:</span> ${step}</div>`).join('')}
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

    showLoading('hastad-demo-loading');
    clearResult('hastad-demo-result');

    try {
        const response = await fetch('/api/generate_hastad_demo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message, e: e, bits: bits, count: count })
        });

        const result = await response.json();
        hideLoading('hastad-demo-loading');

        if (result.success) {
            let keysHTML = '<h4>🔑 Các khóa công khai:</h4>';
            result.keys.forEach((key, index) => {
                keysHTML += `
                    <div class="key-display mb-2">
                        <strong>Khóa ${key.index}:</strong><br>
                        n${key.index} = ${key.n}<br>
                        e${key.index} = ${key.e}
                    </div>
                `;
            });

            let ciphersHTML = '<h4>🔒 Các bản mã:</h4>';
            result.ciphertexts.forEach((cipher, index) => {
                ciphersHTML += `
                    <div class="key-display mb-1">
                        <strong>Bản mã ${index + 1}:</strong> ${cipher}
                    </div>
                `;
            });

            const demoHTML = `
                <h3>📋 Demo Tấn công Håstad đã sẵn sàng!</h3>
                <div class="key-display">
                    <strong>Bản rõ gốc:</strong> "${result.message}"<br>
                    <strong>Số mũ công khai:</strong> ${e}<br>
                    <strong>Số lượng khóa:</strong> ${count}
                </div>
                ${keysHTML}
                ${ciphersHTML}
                <div class="attack-example mt-2">
                    <strong>📝 Lưu ý:</strong> Cùng một bản rõ được mã hóa với ${count} khóa khác nhau có cùng e=${e}. 
                    Bây giờ hãy thực hiện tấn công Håstad bên dưới!
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
        const response = await fetch('/api/attack_hastad', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ciphertexts: ciphertexts, public_keys: publicKeys })
        });

        const result = await response.json();
        hideLoading('hastad-attack-loading');

        if (result.success) {
            let stepsHTML = '<div class="steps-container"><h4>🔍 Các bước tấn công Håstad:</h4>';
            result.steps.forEach((step, index) => {
                stepsHTML += `<div class="step-item"><span class="step-number">Bước ${index + 1}:</span> ${step}</div>`;
            });
            stepsHTML += '</div>';

            const attackHTML = `
                <h3>🎯 Tấn công Håstad thành công!</h3>
                <div class="key-display">
                    <strong>Bản rõ đã khôi phục:</strong> "${result.message}"<br>
                    <strong>Giá trị số nguyên:</strong> ${result.recovered_m}
                </div>
                ${stepsHTML}
                <div class="warning-box mt-2">
                    <strong>🚨 Kết luận:</strong> Không bao giờ gửi cùng một bản rõ tới nhiều người với cùng số mũ e nhỏ!
                </div>
            `;
            showResult('hastad-attack-result', attackHTML, 'success');
        } else {
            const errorHTML = `
                <h3>❌ Tấn công thất bại</h3>
                <p>${result.error}</p>
                ${result.steps ? `
                    <div class="steps-container">
                        <h4>Các bước đã thực hiện:</h4>
                        ${result.steps.map((step, index) => `<div class="step-item"><span class="step-number">Bước ${index + 1}:</span> ${step}</div>`).join('')}
                    </div>
                ` : ''}
            `;
            showResult('hastad-attack-result', errorHTML, 'error');
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