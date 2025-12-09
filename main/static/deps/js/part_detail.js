document.addEventListener('DOMContentLoaded', function() {
    const context = document;

    // --- 1. Вспомогательные функции ---

    // Получение CSRF-токена
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


    // --- 2. ЛОГИКА AJAX КОРЗИНЫ (Добавление и смена кнопки) ---

    function initCartAjax(context) {
        const form = context.querySelector('#add-to-cart-form');
        // 🛑 Ищем родительский контейнер, который нужно заменить целиком
        const purchaseArea = context.querySelector('#part-purchase-area');

        if (form && purchaseArea) {
            const cartUrl = form.dataset.cartUrl;

            form.addEventListener('submit', function(e) {
                e.preventDefault();

                const url = form.action;
                const data = new FormData(form);
                const csrfToken = getCookie('csrftoken');

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
                        // 🟢 УСПЕХ: Вставляем HTML, который идентичен блоку 'else' из шаблона
                        const successHtml = `
                            <div class="row align-items-center mb-4 g-0"> 
                                <div class="col-12 col-md-5 text-center text-md-start mb-2 mb-md-0">
                                    <strong class="text-secondary text-center fs-6">
                                        <i class="fas fa-check-circle"></i> Товар добавлен!
                                    </strong>
                                </div>

                                <div class="col-12 col-md-7 text-md-end">
                                    <a href="${cartUrl}" class="btn btn-success btn-lg">
                                        Перейти к оформлению
                                    </a>
                                </div>
                            </div>
                        `;

                        // 🛑 Заменяем все содержимое контейнера покупки
                        purchaseArea.innerHTML = successHtml;

                        // Обновляем значок корзины в шапке
                        const cartCountEl = document.getElementById('cart-total-count');
                        if (cartCountEl && data.total_quantity !== undefined) {
                            const quantity = parseInt(data.total_quantity);
                            cartCountEl.textContent = quantity;
                            cartCountEl.style.display = (quantity > 0) ? 'inline-block' : 'none';
                        }

                    } else {
                        // 🔴 Ошибка валидации
                        alert('Ошибка при добавлении в корзину: Неверные данные.');
                        console.error('Server Validation Errors:', data.errors);

                        if (submitButton) {
                            submitButton.disabled = false;
                            submitButton.textContent = 'Добавить в корзину';
                        }
                    }
                })
                .catch(error => {
                    console.error('AJAX Error:', error);
                    alert('Произошла критическая ошибка при добавлении в корзину.');

                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.textContent = 'Добавить в корзину';
                    }
                });
            });
        }
    }


    // --- 3. ЛОГИКА И СИНХРОНИЗАЦИЯ КАРУСЕЛЕЙ (Галерея) ---

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

            // 3.1. Логика открытия галереи по клику на изображение превью
            context.querySelectorAll('.js-open-fullscreen').forEach(img => {
                img.addEventListener('click', function() {
                    const slideIndex = this.dataset.slideIndex;
                    fullScreenCarousel.to(parseInt(slideIndex));
                });
            });

            // 3.2. Синхронизация: Модалка -> Превью
            fullScreenCarouselEl.addEventListener('slide.bs.carousel', function (event) {
                if (primaryCarousel) {
                    primaryCarousel.to(event.to);
                }
            });

            // 3.3. Хак: Убедиться, что карусель корректно отображается после открытия модального окна
            imageModalEl.addEventListener('shown.bs.modal', function () {
                fullScreenCarouselEl.dispatchEvent(new Event('resize'));
            });
        }
    }


    // --- 4. Запуск всех функций ---

    initCartAjax(context);
    initCarousels(context);
});