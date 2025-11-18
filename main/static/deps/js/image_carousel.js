document.addEventListener('DOMContentLoaded', function () {
    const mainCarouselEl = document.getElementById('checked_donorImageCarousel');
    const donorfullScreenCarouselEl = document.getElementById('donorfullScreenCarousel');
    const donorimageModalEl = document.getElementById('donorimageModal');

    // 1. При открытии модального окна, синхронизируем индекс слайда
    donorimageModalEl.addEventListener('show.bs.modal', function (event) {
        const activeSlide = mainCarouselEl.querySelector('.carousel-item.active');
        let index = 0;
        if (activeSlide) {
            index = Array.from(mainCarouselEl.querySelectorAll('.carousel-item')).indexOf(activeSlide);
        }

        // Используем getOrCreateInstance для Bootstrap 5.2+
        const bsFullScreenCarousel = bootstrap.Carousel.getOrCreateInstance(donorfullScreenCarouselEl, { interval: false });
        bsFullScreenCarousel.to(index);
    });

    // 2. Синхронизация: Если пользователь листает в модальном окне, обновляем превью-карусель
    donorfullScreenCarouselEl.addEventListener('slide.bs.carousel', function (event) {
        const index = event.to;
        const bsMainCarousel = bootstrap.Carousel.getOrCreateInstance(mainCarouselEl, { interval: false });
        bsMainCarousel.to(index);
    });

    // 3. Небольшой хак: убедиться, что карусель корректно отображается после открытия модального окна
    donorimageModalEl.addEventListener('shown.bs.modal', function () {
        donorfullScreenCarouselEl.dispatchEvent(new Event('resize'));
    });
});