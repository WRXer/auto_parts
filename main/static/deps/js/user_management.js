document.addEventListener('DOMContentLoaded', function() {

    // --- ФУНКЦИЯ ДЛЯ БЛОКИРОВКИ ВСПЛЫТИЯ СОБЫТИЯ ---
    function stopPropagation(event) {
        event.stopPropagation();
    }
    // -----------------------------------------------------------

    // Функция-обработчик для изменения статуса пользователя
    function handleUserStatusChange(event) {
        stopPropagation(event);

        const select = event.target;
        const form = select.closest('form');
        const userId = select.dataset.userId;
        // Для пользователя originalValue - это Boolean
        const originalValue = select.value === 'True';

        const formData = new FormData(form);
        const url = form.action;
        const csrfToken = formData.get('csrfmiddlewaretoken');

        select.disabled = true;

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || `Сервер ответил с ошибкой: ${response.status}`);
                }).catch(() => {
                    throw new Error(`Сервер ответил с ошибкой: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log(`Статус пользователя #${userId} успешно обновлен на ${data.is_active}.`);
            } else {
                throw new Error(data.error || 'Неизвестная ошибка в данных.');
            }
        })
        .catch(error => {
            console.error('Ошибка при обновлении статуса пользователя:', error.message);
            alert(`Ошибка: Не удалось обновить статус пользователя #${userId}. ${error.message}`);

            // Откатываем выбор
            select.value = originalValue ? 'True' : 'False';
        })
        .finally(() => {
            select.disabled = false;
        });
    }


    // --- Обработка смены статусов Пользователей ---
    const userStatusSelects = document.querySelectorAll('.admin-user-status-form select');

    userStatusSelects.forEach(select => {
        // Блокируем mousedown/click, чтобы избежать конфликтов с другими событиями
        select.addEventListener('mousedown', stopPropagation);
        select.addEventListener('click', stopPropagation);

        // Вызываем handleUserStatusChange при смене значения
        select.addEventListener('change', handleUserStatusChange);
    });
});