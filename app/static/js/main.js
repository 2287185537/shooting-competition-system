// 在页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 自动隐藏提示消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.classList.remove('show');
            setTimeout(function() {
                alert.remove();
            }, 150);
        }, 3000);
    });

    // 表单验证
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // 比赛报名表单处理
    const registrationForm = document.querySelector('#registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(event) {
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 处理中...';
        });
    }

    // 成绩输入验证
    const scoreInputs = document.querySelectorAll('input[type="number"][name="score"]');
    scoreInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0) {
                this.value = 0;
            } else if (value > 100) {
                this.value = 100;
            }
        });
    });

    // 密码强度检查
    const passwordInput = document.querySelector('input[name="password"]');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            
            // 长度检查
            if (password.length >= 8) strength++;
            // 包含数字
            if (/\d/.test(password)) strength++;
            // 包含字母
            if (/[a-zA-Z]/.test(password)) strength++;
            // 包含特殊字符
            if (/[^A-Za-z0-9]/.test(password)) strength++;

            const feedbackElement = this.nextElementSibling;
            if (feedbackElement) {
                switch (strength) {
                    case 0:
                    case 1:
                        feedbackElement.textContent = '密码强度：弱';
                        feedbackElement.className = 'text-danger';
                        break;
                    case 2:
                    case 3:
                        feedbackElement.textContent = '密码强度：中';
                        feedbackElement.className = 'text-warning';
                        break;
                    case 4:
                        feedbackElement.textContent = '密码强度：强';
                        feedbackElement.className = 'text-success';
                        break;
                }
            }
        });
    }

    // 日期时间输入处理
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        // 设置最小日期为今天
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
    });

    // 确认对话框
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm(this.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    // 表格排序
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(function(header) {
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            const index = Array.from(this.parentNode.children).indexOf(this);
            const isNumeric = this.dataset.sort === 'numeric';
            const isAsc = this.classList.contains('asc');

            rows.sort(function(a, b) {
                const aVal = a.children[index].textContent;
                const bVal = b.children[index].textContent;
                if (isNumeric) {
                    return isAsc ? parseFloat(bVal) - parseFloat(aVal) : parseFloat(aVal) - parseFloat(bVal);
                }
                return isAsc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
            });

            this.classList.toggle('asc');
            table.querySelector('tbody').append(...rows);
        });
    });
});