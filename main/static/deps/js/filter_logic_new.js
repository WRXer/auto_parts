// filter_logic_new.js

// Читаем PK категории из глобального объекта, который мы объявим в HTML
const CATEGORY_PK = window.FilterConfig ? window.FilterConfig.categoryPk : null;

/**
 * Применяет изменения фильтра, обрабатывает каскадный сброс и перезагружает страницу.
 * @param {string} keyToChange - Ключ фильтра (make, model, generation).
 * @param {string} valueToChange - Новое значение PK, или пустая строка для сброса.
 */
function applyFilterChange(keyToChange, valueToChange) {
    const url = new URL(window.location.href);

    // 1. Устанавливаем или удаляем текущий ключ
    if (valueToChange) {
        url.searchParams.set(keyToChange, valueToChange);
    } else {
        url.searchParams.delete(keyToChange);
    }

    // 2. Добавляем ID категории из глобальной конфигурации
    if (CATEGORY_PK) {
        url.searchParams.set('category', CATEGORY_PK);
    }

    // 3. КАСКАДНЫЙ СБРОС

    // Если меняем Марку, сбрасываем Модель и Модификацию
    if (keyToChange === 'make') {
        url.searchParams.delete('model');
        url.searchParams.delete('generation');
    }

    // Если меняем Модель, сбрасываем Модификацию
    if (keyToChange === 'model') {
        url.searchParams.delete('generation');
    }

    // 4. Перезагружаем страницу
    window.location.href = url.toString();
}

/**
 * Обработчик изменения SELECT (выпадающие списки)
 */
function filterChange(selectElement) {
    const selectedKey = selectElement.name;
    const selectedValue = selectElement.value;

    if (selectedKey !== 'make' && selectedKey !== 'model' && selectedKey !== 'generation') {
        console.error("Ошибка: Неверный атрибут name у SELECT-тега.");
        return;
    }

    applyFilterChange(selectedKey, selectedValue);
}
