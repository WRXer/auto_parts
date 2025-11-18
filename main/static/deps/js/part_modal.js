document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('partDetailModal');

    // Выходим, если основной элемент модального окна не найден
    if (!modalElement) {
        console.error("Критическая ошибка: Элемент #partDetailModal не найден.");
        return;
    }

    // Инициализируем основное модальное окно
    const partDetailModal = new bootstrap.Modal(modalElement, { keyboard: true });

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

    document.querySelectorAll('.js-open-part-modal').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.dataset.url;
            this.blur();

            // Находим контейнер для вставки контента
            const modalDialog = modalElement.querySelector('.modal-dialog');
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
        });
    });

    // =========================================================
    // 2. ИНИЦИАЛИЗАЦИЯ ДИНАМИЧЕСКОГО КОНТЕНТА
    // =========================================================

    // context — это элемент .modal-dialog, куда вставлен фрагмент
    function initDynamicContent(context) {
        // Инициализация каруселей и галереи
        initCarousels(context);

        // Инициализация AJAX-логики для формы корзины
        initCartAjax(context, partDetailModal);
    }

    // =========================================================
    // 3. ИНИЦИАЛИЗАЦИЯ И СИНХРОНИЗАЦИЯ КАРУСЕЛЕЙ
    // =========================================================

    function initCarousels(context) {
        const mainCarouselEl = context.querySelector('#donorImageCarousel');
        const fullScreenCarouselEl = context.querySelector('#fullScreenCarousel');
        const imageModalEl = context.querySelector('#imageModal');

        let primaryCarousel;

        // Инициализация основной карусели
        if (mainCarouselEl) {
            primaryCarousel = new bootstrap.Carousel(mainCarouselEl, { interval: false });
        }

        // Инициализация полноэкранной галереи и синхронизация
        if (fullScreenCarouselEl && imageModalEl) {

            const fullScreenCarousel = new bootstrap.Carousel(fullScreenCarouselEl, { interval: false });
            const imageModal = new bootstrap.Modal(imageModalEl);

            // Логика открытия галереи по клику на изображение
            context.querySelectorAll('.js-open-fullscreen').forEach(img => {
                img.addEventListener('click', function() {
                    const slideIndex = this.dataset.slideIndex;
                    fullScreenCarousel.to(parseInt(slideIndex));
                    imageModal.show();
                });
            });

            // Синхронизация: Модалка -> Превью
            fullScreenCarouselEl.addEventListener('slide.bs.carousel', function (event) {
                if (primaryCarousel) {
                    primaryCarousel.to(event.to);
                }
            });

            // Хак: Убедиться, что карусель корректно отображается
            imageModalEl.addEventListener('shown.bs.modal', function () {
                fullScreenCarouselEl.dispatchEvent(new Event('resize'));
            });

            // Сброс состояния
            imageModalEl.addEventListener('hidden.bs.modal', function () {
                document.activeElement.blur();
            });
        }
    }

    // =========================================================
    // 4. ЛОГИКА AJAX КОРЗИНЫ (Добавление и смена кнопки)
    // =========================================================

    function initCartAjax(context, mainModal) {
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
                            cartCountEl.textContent = data.total_quantity;
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