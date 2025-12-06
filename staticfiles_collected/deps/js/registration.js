// /deps/js/registration.js

document.addEventListener('DOMContentLoaded', function() {
    // 1. Получаем элемент с данными (из HTML)
    const dataElement = document.getElementById('registration-data');

    // Проверяем, установлен ли флаг успешной регистрации
    if (dataElement && dataElement.dataset.successful === 'true') {
        const userEmail = dataElement.dataset.userEmail;
        const redirectUrl = dataElement.dataset.redirectUrl; // Должен быть "/"

        // Находим элементы модального окна
        const modalElement = document.getElementById('activationModal');
        const modalEmailSpan = document.getElementById('modal-email');
        const modalOkButton = document.getElementById('modal-ok-button');

        if (modalElement) {
            // Устанавливаем email в модальное окно для информации
            if (modalEmailSpan) {
                modalEmailSpan.textContent = userEmail;
            }

            // 2. Показываем модальное окно (требует, чтобы Bootstrap JS был загружен)
            const activationModal = new bootstrap.Modal(modalElement);
            activationModal.show();

            // 3. Добавляем обработчик для кнопки "ОК"
            if (modalOkButton) {
                modalOkButton.addEventListener('click', function() {
                    // Перенаправляем на главную страницу
                    window.location.href = redirectUrl;
                });
            }
        }
    }
});