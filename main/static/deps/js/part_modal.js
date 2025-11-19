document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('partDetailModal');

    // Выходим, если основной элемент модального окна не найден
    if (!modalElement) {
        console.error("Критическая ошибка: Элемент #partDetailModal не найден.");
        return;
    }

    // Инициализируем основное модальное окно
    const partDetailModal = new bootstrap.Modal(modalElement, { keyboard: true });
    const modalDialog = modalElement.querySelector('.modal-dialog');

    // Функция для получения CSRF-токена из куки
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // =========================================================
    // 1. ЛОГИКА ОТКРЫТИЯ МОДАЛЬНОГО ОКНА ДЕТАЛЕЙ (AJAX)
    // =========================================================

    document.body.addEventListener('click', function(e) {
        const button = e.target.closest('.js-open-part-modal');
        if (button) {
            e.preventDefault();
            const url = button.dataset.url;
            button.blur();

            if (modalDialog) {
                // Показываем заглушку
                modalDialog.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header"><h5 class="modal-title">Загрузка...</h5><button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button></div>
                        <div class="modal-body text-center py-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Загрузка...</span></div><p class="mt-2">Пожалуйста, подождите...</p></div>
                    </div>`;
                partDetailModal.show();

                // AJAX запрос
                fetch(url)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.text();
                    })
                    .then(html => {
                        // Вставляем HTML-фрагмент (перезаписывая заглушку)
                        modalDialog.innerHTML = html;
                        // Инициализируем весь новый динамический контент
                        initDynamicContent(modalDialog);
                    })
                    .catch(error => {
                        console.error('Ошибка при загрузке данных:', error);
                        // Выводим сообщение об ошибке
                        modalDialog.innerHTML =
                            `<div class="modal-content">
                                <div class="modal-header"><h5 class="modal-title text-danger">Ошибка</h5><button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button></div>
                                <div class="modal-body text-danger">Не удалось загрузить данные запчасти: ${error.message}</div>
                            </div>`;
                    });
            } else {
                 console.error("Ошибка: Не найден .modal-dialog внутри #partDetailModal.");
            }
        }
    });

    // =========================================================
    // 2. ИНИЦИАЛИЗАЦИЯ ДИНАМИЧЕСКОГО КОНТЕНТА
    // =========================================================

    // context — это элемент .modal-dialog, куда вставлен фрагмент
    function initDynamicContent(context) {
        // Инициализация каруселей и галереи
        initCarousels(context);

        // Инициализация AJAX-логики для формы корзины
        initCartAjax(context);
    }

    // =========================================================
    // 3. ИНИЦИАЛИЗАЦИЯ И СИНХРОНИЗАЦИЯ КАРУСЕЛЕЙ
    // =========================================================

    function initCarousels(context) {
        // Логика каруселей должна быть адаптирована под ID,
        // которые используются в загружаемом фрагменте (если они есть).

        // ВАЖНО: Убедитесь, что ID ваших каруселей в фрагменте (например, #partImageCarousel)
        // не конфликтуют с ID каруселей донора.

        // Пример инициализации основной карусели в фрагменте
        const partCarouselEl = context.querySelector('#partImageCarousel');
        if (partCarouselEl) {
            new bootstrap.Carousel(partCarouselEl, { interval: false });
        }
    }

    // =========================================================
    // 4. ЛОГИКА AJAX КОРЗИНЫ (Добавление и смена кнопки)
    // =========================================================

    function initCartAjax(context) {
        const form = context.querySelector('#add-to-cart-form');
        const buttonContainer = context.querySelector('#add-to-cart-button-container');

        if (form && buttonContainer) {

            // 🔑 ПОЛУЧАЕМ URL КОРЗИНЫ ИЗ DATA-АТРИБУТА
            const cartUrl = form.dataset.cartUrl;

            form.addEventListener('submit', function(e) {
                e.preventDefault();

                const url = form.action;
                const data = new FormData(form);
                const csrfToken = getCookie('csrftoken');

                // Получаем кнопку для управления состоянием
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.textContent = 'Обработка...';
                }

                fetch(url, {
                    method: 'POST',
                    body: data,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken
                    }
                })
                .then(response => {
                    if (!response.ok && response.status !== 400) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        // 🟢 УСПЕХ: Вставляем новый блок Статус + Кнопка оформления
                        buttonContainer.innerHTML = `
                            <div class="row align-items-center w-100 g-0"> 
                                <div class="col-3 text-left">
                                    <strong class="text-secondary fs-7">
                                        <i class="fas fa-check-circle"></i> Товар добавлен!
                                    </strong>
                                </div>
                                
                                <div class="col-9 text-end"> 
                                    <a href="${cartUrl}" class="btn btn-success btn-lg">
                                        Перейти к оформлению
                                    </a>
                                </div>
                            </div>
                        `;

                        // 🔑 Здесь можно добавить код для обновления значка корзины в шапке
                        const cartCountEl = document.getElementById('cart-total-count');
                        if (cartCountEl && data.total_quantity !== undefined) {
                            const quantity = parseInt(data.total_quantity);

                            // Обновляем текст
                            cartCountEl.textContent = quantity;

                            // Управляем видимостью (скрываем при 0, показываем при > 0)
                            if (quantity > 0) {
                                cartCountEl.style.display = 'inline-block';
                            } else {
                                cartCountEl.style.display = 'none';
                            }
                        }

                    } else {
                        // 🔴 Ошибка валидации
                        alert('Ошибка при добавлении в корзину: Неверные данные.');
                        console.error('Server Validation Errors:', data.errors);

                        // Возвращаем кнопку в исходное состояние
                        if (submitButton) {
                            submitButton.disabled = false;
                            submitButton.textContent = 'Добавить в корзину';
                        }
                    }
                })
                .catch(error => {
                    console.error('AJAX Error:', error);
                    alert('Произошла критическая ошибка при добавлении в корзину.');

                    // Возвращаем кнопку в исходное состояние
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.textContent = 'Добавить в корзину';
                    }
                });
            });
        }
    }
});