document.addEventListener('DOMContentLoaded', function () {
    const mainCarouselEl = document.getElementById('donorImageCarousel');
    const fullScreenCarouselEl = document.getElementById('fullScreenCarousel');
    const imageModalEl = document.getElementById('imageModal');

    // 1. При открытии модального окна, синхронизируем индекс слайда
    imageModalEl.addEventListener('show.bs.modal', function (event) {
        const activeSlide = mainCarouselEl.querySelector('.carousel-item.active');
        let index = 0;
        if (activeSlide) {
            index = Array.from(mainCarouselEl.querySelectorAll('.carousel-item')).indexOf(activeSlide);
        }

        // Используем getOrCreateInstance для Bootstrap 5.2+
        const bsFullScreenCarousel = bootstrap.Carousel.getOrCreateInstance(fullScreenCarouselEl, { interval: false });
        bsFullScreenCarousel.to(index);
    });

    // 2. Синхронизация: Если пользователь листает в модальном окне, обновляем превью-карусель
    fullScreenCarouselEl.addEventListener('slide.bs.carousel', function (event) {
        const index = event.to;
        const bsMainCarousel = bootstrap.Carousel.getOrCreateInstance(mainCarouselEl, { interval: false });
        bsMainCarousel.to(index);
    });

    // 3. Небольшой хак: убедиться, что карусель корректно отображается после открытия модального окна
    imageModalEl.addEventListener('shown.bs.modal', function () {
        fullScreenCarouselEl.dispatchEvent(new Event('resize'));
    });
});