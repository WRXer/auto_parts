document.addEventListener('DOMContentLoaded', function() {

    // --- ФУНКЦИЯ ДЛЯ БЛОКИРОВКИ ВСПЛЫТИЯ СОБЫТИЯ ---
    function stopAccordionAction(event) {
        // Останавливаем всплытие, чтобы избежать активации родительской кнопки аккордеона.
        event.stopPropagation();
    }
    // -----------------------------------------------------------


    // Функция-обработчик для отправки AJAX-запроса
    function handleStatusChange(event) {
        // Блокируем сворачивание
        stopAccordionAction(event);

        const select = event.target;
        const form = select.closest('form');
        const orderId = select.dataset.orderId;
        const originalValue = select.value;
        const formClass = form.classList.contains('admin-paid-form') ? 'paid' : 'status';


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
            // Если ответ не 2xx, обрабатываем как ошибку
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || `Сервер ответил с ошибкой: ${response.status}`);
                }).catch(() => {
                    throw new Error(`Сервер ответил с ошибкой: ${response.status}`);
                });
            }

            // Защита от пустого/невалидного JSON-ответа
            return response.text().then(text => {
                try {
                    return text ? JSON.parse(text) : {};
                } catch (e) {
                    throw new Error(`Не удалось распарсить JSON. Ответ сервера: "${text.substring(0, 50)}..."`);
                }
            });
        })
        .then(data => {
            if (data.success) {
                console.log(`Статус заказа #${orderId} (${formClass}) успешно обновлен.`);

                // Обновляем отображение оплаты, используя ID
                if (formClass === 'paid') {
                    const statusText = data.is_paid ? ' Оплачен' : ' Не оплачен';

                    // Использование document.getElementById для надежного поиска
                    const paidParagraph = document.getElementById(`paid-status-${orderId}`);

                    if (paidParagraph) {
                         paidParagraph.innerHTML = `<span class="fw-bold">Оплата:</span>${statusText}`;
                    } else {
                         console.warn(`Элемент #paid-status-${orderId} не найден для обновления.`);
                    }
                }

            } else {
                throw new Error(data.error || 'Неизвестная ошибка в данных.');
            }
        })
        .catch(error => {
            console.error('Ошибка при обновлении статуса:', error.message);
            // Выводим alert только для реальных сетевых/серверных ошибок
            if (!error.message.includes('Не удалось распарсить JSON')) {
                 alert(`Ошибка: Не удалось обновить статус заказа #${orderId}.`);
            } else {
                 console.warn("Произошла ошибка парсинга JSON, но запрос, возможно, был успешным.");
            }
            // Откатываем выбор
            select.value = originalValue;
        })
        .finally(() => {
            select.disabled = false;
        });
    }

    // --- 1. Обработка смены статусов (AJAX и блокировка) ---
    const allSelects = document.querySelectorAll('.admin-status-form select, .admin-paid-form select');

    allSelects.forEach(select => {
        // Блокируем mousedown/click для предотвращения сворачивания аккордеона
        select.addEventListener('mousedown', stopAccordionAction);
        select.addEventListener('click', stopAccordionAction);

        // Вызываем handleStatusChange при смене значения
        select.addEventListener('change', handleStatusChange);
    });

    // --- 2. Визуальное выделение активного заказа ---
    const adminAccordion = document.getElementById('adminOrdersAccordion');

    if (adminAccordion) {
        // Событие: Заказ начинает открываться (SHOWING)
        adminAccordion.addEventListener('show.bs.collapse', function(event) {
            const accordionItem = event.target.closest('.accordion-item');
            if (accordionItem) {
                // Добавляем класс, который мы стилизовали в CSS
                accordionItem.classList.add('order-active');
            }
        });

        // Событие: Заказ начинает закрываться (HIDING)
        adminAccordion.addEventListener('hide.bs.collapse', function(event) {
            const accordionItem = event.target.closest('.accordion-item');
            if (accordionItem) {
                // Удаляем класс
                accordionItem.classList.remove('order-active');
            }
        });
    }
});