document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('partRequestFormCollapse');
    const collapseElement = document.getElementById('requestFormCollapse');
    const toggleButton = document.querySelector('.fixed-bottom-right-accordion button.toggle-button');
    if (!form || !collapseElement || !toggleButton) return;

    // Инициализируем объект collapse Bootstrap
    const collapseInstance = new bootstrap.Collapse(collapseElement, {
        toggle: false
    });

    // 1. Обработка отправки формы (ВАШ СУЩЕСТВУЮЩИЙ КОД)
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const messageDiv = document.getElementById('formMessageCollapse');
        const submitButton = form.querySelector('button[type="submit"]');

        submitButton.disabled = true;
        submitButton.textContent = 'Отправка...';
        messageDiv.style.display = 'none';

        fetch(form.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json().then(data => ({status: response.status, body: data})))
        .then(result => {
            submitButton.disabled = false;
            submitButton.textContent = 'Отправить заявку';

            if (result.status === 200 && result.body.success) {
                messageDiv.innerHTML = '<i class="fas fa-check-circle"></i> Отправлено! В ближайшее время наш менеджер свяжется с Вами!';
                messageDiv.className = 'mt-2 small text-warning fw-bold';
                messageDiv.style.display = 'block';
                form.reset();

                // Закрыть аккордеон через 3 секунды
                setTimeout(() => {
                    collapseInstance.hide(); // Используем инстанс
                }, 3000);

            } else {
                let errorText = 'Ошибка отправки';
                if (result.body.errors) {
                    errorText = Object.values(result.body.errors).join(', ');
                } else if (result.body.detail) {
                     errorText = result.body.detail;
                }
                messageDiv.textContent = errorText;
                messageDiv.className = 'mt-2 small text-danger';
                messageDiv.style.display = 'block';
            }
        })
        .catch((error) => {
            console.error('Fetch error:', error);
            submitButton.disabled = false;
            submitButton.textContent = 'Отправить заявку';
            messageDiv.textContent = 'Ошибка соединения с сервером';
            messageDiv.className = 'mt-2 small text-danger';
            messageDiv.style.display = 'block';
        });
    });

    // 2. СВОРЧИВАНИЕ ПО КЛИКУ ВНЕ ФОРМЫ (НОВЫЙ КОД)
    document.body.addEventListener('click', function(event) {
        // Проверяем, открыта ли форма
        if (collapseElement.classList.contains('show')) {
            const isClickInsideAccordion = collapseElement.contains(event.target);
            const isClickOnToggleButton = toggleButton.contains(event.target);

            // Если клик не внутри формы И не на кнопке-переключателе
            if (!isClickInsideAccordion && !isClickOnToggleButton) {
                // Скрываем форму
                collapseInstance.hide();
            }
        }
    });
});