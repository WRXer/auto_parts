document.addEventListener('DOMContentLoaded', function() {
    const track = document.getElementById('reviews-track');
    // Константы
    const REVIEWS_TO_SHOW = 3;
    const INTERVAL_TIME = 4000; // 4 секунды
    const TRANSITION_DURATION = 700; // 0.7 секунды
    const GAP_SIZE = 16; // 1rem

    let reviews = [];
    let currentIndex = 0;

    // ВНИМАНИЕ: Путь к reviews.json теперь должен быть абсолютным или относительным
    // к корню сайта, так как мы не можем использовать тег {% static %} внутри JS файла.
    // Если static files настроены стандартно, /static/reviews.json будет работать.
    // Если Django настроен специфично, возможно, потребуется передать путь через data-атрибут в HTML.
    // Для стандартной настройки используем относительный путь:
    const REVIEWS_URL = '/static/reviews.json';

    // --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

    /**
     * Перемешивает массив (алгоритм Фишера–Йетса).
     * @param {Array} array
     * @returns {Array} Перемешанный массив.
     */
    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    function createReviewCard(review) {
        const stars = Array(review.rating).fill('<i class="fas fa-star text-warning"></i>').join('');

        return `
            <div class="review-card card p-3 shadow-sm flex-shrink-0 rounded-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="fw-bold text-dark">${review.author}</span>
                    <small class="text-muted">${review.date}</small>
                </div>
                <div class="mb-2">${stars}</div>
                <p class="card-text small mb-0">
                    ${review.text}
                </p>
            </div>
        `;
    }

    function renderInitialReviews() {
        track.innerHTML = '';
        for (let i = 0; i < REVIEWS_TO_SHOW; i++) {
            const review = reviews[i % reviews.length];
            track.innerHTML += createReviewCard(review);
        }
        currentIndex = REVIEWS_TO_SHOW % reviews.length;
    }

    function startReviewRotation() {
        if (!track.firstElementChild) return;

        // Ширина карточки + отступ справа (16px)
        const cardWidth = track.firstElementChild.offsetWidth + GAP_SIZE;

        setInterval(() => {
            // 1. Анимация: сдвиг влево
            track.style.transition = `transform ${TRANSITION_DURATION}ms ease-in-out`;
            track.style.transform = `translateX(-${cardWidth}px)`;

            // 2. Смена элементов после анимации
            setTimeout(() => {
                const newReview = reviews[currentIndex];
                const newCardHTML = createReviewCard(newReview);

                // Удаляем старый отзыв (первый элемент)
                if (track.firstElementChild) {
                    track.removeChild(track.firstElementChild);
                }

                // Добавляем новый отзыв в конец трека
                track.innerHTML += newCardHTML;

                // Сброс трансформации и анимации для мгновенного "телепорта"
                track.style.transition = 'none';
                track.style.transform = 'translateX(0)';

                // Обновляем индекс: циклический переход
                currentIndex = (currentIndex + 1) % reviews.length;

            }, TRANSITION_DURATION);

        }, INTERVAL_TIME);
    }

    // --- ЗАПУСК: Загрузка данных, перемешивание и старт ---

    fetch(REVIEWS_URL)
        .then(response => {
            if (!response.ok) {
                // Если стандартный путь не сработал, попробуем путь, переданный через data-атрибут,
                // если вы решите его использовать (см. ниже).
                console.warn('Не удалось загрузить отзывы по стандартному пути /static/reviews.json');
                throw new Error('Не удалось загрузить reviews.json: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            reviews = shuffleArray(data);

            if (reviews.length >= REVIEWS_TO_SHOW) {
                renderInitialReviews();
                startReviewRotation();
            } else if (reviews.length > 0) {
                renderInitialReviews();
            } else {
                track.innerHTML = '<p class="text-center text-muted">Отзывов пока нет.</p>';
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки отзывов:', error);
            track.innerHTML = '<p class="text-center text-danger">Не удалось загрузить отзывы.</p>';
        });
});