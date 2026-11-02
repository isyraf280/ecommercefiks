// Authentication Interactive Features
document.addEventListener('DOMContentLoaded', () => {
    // 1. Password Visibility Toggle
    const toggleButtons = document.querySelectorAll('.btn-toggle-pwd');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = btn.getAttribute('data-target');
            const pwdInput = document.getElementById(targetId);
            if (!pwdInput) return;

            const isPassword = pwdInput.type === 'password';
            pwdInput.type = isPassword ? 'text' : 'password';

            // Update SVG icon
            const iconEye = btn.querySelector('.icon-eye');
            const iconEyeSlash = btn.querySelector('.icon-eye-slash');
            if (iconEye && iconEyeSlash) {
                if (isPassword) {
                    iconEye.style.display = 'none';
                    iconEyeSlash.style.display = 'block';
                } else {
                    iconEye.style.display = 'block';
                    iconEyeSlash.style.display = 'none';
                }
            }
        });
    });

    // 2. Alert Dismissal with smooth fade out
    const alertCloses = document.querySelectorAll('.alert-close');
    alertCloses.forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            if (alert) {
                alert.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });

    // 3. Form Submit Loading Spinner
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('.btn-submit');
            if (submitBtn && form.checkValidity()) {
                submitBtn.classList.add('loading');
                const btnText = submitBtn.querySelector('.btn-text');
                if (btnText) {
                    btnText.setAttribute('data-original-text', btnText.textContent);
                    btnText.textContent = submitBtn.getAttribute('data-loading-text') || 'Memproses...';
                }
            }
        });
    });

    // 4. Password Confirmation check (for register)
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm_password');

        if (passwordInput && confirmPasswordInput) {
            function validatePasswordMatch() {
                if (confirmPasswordInput.value && passwordInput.value !== confirmPasswordInput.value) {
                    confirmPasswordInput.setCustomValidity('Konfirmasi password tidak cocok');
                } else {
                    confirmPasswordInput.setCustomValidity('');
                }
            }

            passwordInput.addEventListener('input', validatePasswordMatch);
            confirmPasswordInput.addEventListener('input', validatePasswordMatch);
        }
    }
});
