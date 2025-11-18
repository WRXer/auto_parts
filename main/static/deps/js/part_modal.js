document.addEventListener('DOMContentLoaded', function() {
    const modalElement = document.getElementById('partDetailModal');
    const partDetailModal = new bootstrap.Modal(modalElement);

    // Слушатель для кнопок открытия модального окна запчасти
document.querySelectorAll('.js-open-part-modal').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const url = this.dataset.url;

        // 🔑 1. Снимаем фокус с кнопки, чтобы избежать эффекта "свечения" в навигации
        this.blur();

        // 2. Показываем заглушку
        modalElement.querySelector('.modal-dialog').innerHTML = `
            <div class="modal-content"><div class="modal-header"><h5 class="modal-title">Загрузка...</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body">Пожалуйста, подождите...</div></div>`;
        partDetailModal.show();

        // 3. AJAX запрос
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // 4. Вставляем HTML внутрь modal-dialog
                modalElement.querySelector('.modal-dialog').innerHTML = data.html;

                // 5. Инициализация всех новых компонентов Bootstrap
                const newModalContent = modalElement.querySelector('.modal-content');

                const mainCarouselEl = newModalContent.querySelector('#donorImageCarousel');
                const fullScreenCarouselEl = newModalContent.querySelector('#fullScreenCarousel');
                const imageModalEl = newModalContent.querySelector('#imageModal');

                let primaryCarousel, fullScreenCarousel, imageModal;

                // 5a. Инициализация основной карусели
                if (mainCarouselEl) {
                    primaryCarousel = new bootstrap.Carousel(mainCarouselEl, { interval: false });
                }

                // 5b. Инициализация полноэкранной галереи
                if (fullScreenCarouselEl && imageModalEl) {
                    fullScreenCarousel = new bootstrap.Carousel(fullScreenCarouselEl, { interval: false });
                    imageModal = new bootstrap.Modal(imageModalEl);

                    // 6. Логика открытия галереи и синхронизации
                    newModalContent.querySelectorAll('.js-open-fullscreen').forEach(img => {
                        img.addEventListener('click', function() {
                            const slideIndex = this.dataset.slideIndex;

                            fullScreenCarousel.to(parseInt(slideIndex));

                            // Открытие модального окна галереи
                            imageModal.show();
                        });
                    });

                    // 7. Логика синхронизации: Если листают полноэкранную карусель, обновляем основную
                    fullScreenCarouselEl.addEventListener('slide.bs.carousel', function (event) {
                        if (primaryCarousel) {
                            primaryCarousel.to(event.to);
                        }
                    });

                    // 8. Хак: Убедиться, что карусель корректно отображается после открытия
                    imageModalEl.addEventListener('shown.bs.modal', function () {
                        fullScreenCarouselEl.dispatchEvent(new Event('resize'));
                    });

                    // 9. Сброс состояния при закрытии модальной галереи
                    imageModalEl.addEventListener('hidden.bs.modal', function () {
                        // Сброс фокуса при закрытии второго модального окна
                        document.activeElement.blur();
                    });
                }
            })
            .catch(error => {
                console.error('Ошибка при загрузке данных:', error);
                // Выводим сообщение об ошибке
                modalElement.querySelector('.modal-dialog').innerHTML =
                    `<div class="modal-content">
                        <div class="modal-header"><h5 class="modal-title text-danger">Ошибка</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                        <div class="modal-body text-danger">Не удалось загрузить данные запчасти: ${error.message}</div>
                    </div>`;
            });
        });
    });
});
// Запрет скролла и кликов по фону, пока открыта модалка
document.addEventListener('DOMContentLoaded', function () {
    const modalElement = document.getElementById('partDetailModal');

    modalElement.addEventListener('shown.bs.modal', () => {
        document.body.classList.add('modal-open-fixed');
    });

    modalElement.addEventListener('hidden.bs.modal', () => {
        document.body.classList.remove('modal-open-fixed');
    });
});