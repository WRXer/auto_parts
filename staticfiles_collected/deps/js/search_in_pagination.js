// Этот скрипт гарантирует, что все параметры (part_number, make, model и т.д.)
// будут сохранены при переходе по страницам, чтобы не терялись фильтры.
document.addEventListener('DOMContentLoaded', function() {
    const paginationContainer = document.getElementById('pagination-links');
    if (!paginationContainer) {
        return;
    }

    // 1. Получаем все текущие параметры URL (кроме 'page')
    const currentParams = new URLSearchParams(window.location.search);

    // Удаляем параметр 'page', чтобы он не дублировался
    currentParams.delete('page');

    // Преобразуем оставшиеся параметры в строку
    let preservedQueryString = currentParams.toString();
    if (preservedQueryString) {
        // Добавляем '&' перед другими параметрами, если они есть
        preservedQueryString = '&' + preservedQueryString;
    }

    // 2. Находим все ссылки пагинации с атрибутом data-page
    const links = paginationContainer.querySelectorAll('a[data-page]');

    // 3. Обновляем href для каждой ссылки
    links.forEach(link => {
        const pageNumber = link.getAttribute('data-page');

        // Убеждаемся, что номер страницы валиден (не None/undefined)
        // pageNumber === 'None' может приходить из previous_page_number или next_page_number,
        // когда страница не существует (например, предыдущей страницы нет)
        if (link.getAttribute('href') !== '#' && pageNumber && pageNumber !== 'None') {
            // Собираем URL в формате: ?page=N&param1=val1&param2=val2
            link.href = `?page=${pageNumber}${preservedQueryString}`;
        }
    });
});