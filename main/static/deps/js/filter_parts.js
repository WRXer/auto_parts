 /**
 * Сбрасывает параметр 'category' из URL и перезагружает страницу.
 * Используется для кнопки "Все категории".
 */
    function clearCategoryFilter(event) {
        // Отменяем стандартное действие ссылки (переход на #)
        event.preventDefault();

        // Получаем текущий URL
        const url = new URL(window.location.href);

        // Удаляем параметр 'category'
        url.searchParams.delete('category');

        // Удаляем параметр 'page' (если вы хотите возвращаться на первую страницу)
        // Если вы хотите остаться на текущей странице пагинации, закомментируйте эту строку:
        // url.searchParams.delete('page');

        // Выполняем переход на новый, чистый URL
        window.location.href = url.toString();
    }

    // Сброс пагинации
function clearCategoryFilter(event) {
    event.preventDefault();
    const url = new URL(window.location.href);
    url.searchParams.delete('category');
    url.searchParams.delete('page');  // Сбрасываем пагинацию
    window.location.href = url.pathname;  // Переход без query-параметров
}

