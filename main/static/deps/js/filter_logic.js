// static/js/filter_logic.js
// Управляет каскадными выпадающими списками (Марка -> Модель -> Генерация)
// Динамически устанавливает ACTION формы, используя PK для навигации.

document.addEventListener('DOMContentLoaded', function() {
    const makeSelect = document.getElementById('id_make');
    const modelSelect = document.getElementById('id_model');
    const generationSelect = document.getElementById('id_generation');
    const filterForm = document.getElementById('filter-form');
    const submitButton = document.getElementById('submit-filter-btn');

    // Получаем URL-адреса из HTML-элемента
    const loadModelsUrl = makeSelect.getAttribute('data-load-models-url');
    const loadGenerationsUrl = makeSelect.getAttribute('data-load-generations-url');

    const modelsListUrlTemplate = makeSelect.getAttribute('data-car-model-list-url');
    const generationsListUrlTemplate = makeSelect.getAttribute('data-car-generation-list-url');

    const partsByGenerationUrlTemplate = makeSelect.getAttribute('data-parts-by-generation-url');
    const finalCatalogUrl = makeSelect.getAttribute('data-default-action');


    // =========================================================================
    // ФУНКЦИИ AJAX: Загрузка данных
    // =========================================================================

    function populateSelect(selectElement, data, defaultOptionText) {
        selectElement.innerHTML = `<option value="">-- ${defaultOptionText} --</option>`;
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name;
            selectElement.appendChild(option);
        });
        selectElement.disabled = (data.length === 0);
    }

    function loadModels(makeId) {
        // ИСПРАВЛЕНИЕ: make_id вместо make
        fetch(`${loadModelsUrl}?make_id=${makeId}`)
            .then(response => response.json())
            .then(data => populateSelect(modelSelect, data, "Выберите модель"))
            .catch(error => console.error('Error loading models:', error));
    }

    function loadGenerations(modelId) {
        // ИСПРАВЛЕНИЕ: model_id вместо model
        fetch(`${loadGenerationsUrl}?model_id=${modelId}`)
            .then(response => response.json())
            .then(data => populateSelect(generationSelect, data, "Выберите модификацию"))
            .catch(error => console.error('Error loading generations:', error));
    }


    // =========================================================================
    // 💥 ГЛАВНАЯ ЛОГИКА: Обновление ACTION формы (С ИСПРАВЛЕННОЙ ЗАМЕНОЙ)
    // =========================================================================

    function updateFormAction() {

        const makeId = makeSelect.value;
        // ЛОГ №2: Значение, которое используется для построения URL
        console.log('[LOG 2: Action Builder] Значение makeId для URL:', makeId);

        const modelId = modelSelect.value;
        const generationId = generationSelect.value;

        let newAction = finalCatalogUrl;

        if (generationId) {
            // СЛУЧАЙ 3: Выбрана Генерация -> ФИНАЛЬНЫЙ КАТАЛОГ (3 PK)
            if (partsByGenerationUrlTemplate) {

                let actionWithAllPks = partsByGenerationUrlTemplate
                    // 🚨 ИСПРАВЛЕНИЕ 1: Заменяем ПЕРВЫЙ '/0/' на /makeId/
                    .replace('/0/', `/${makeId}/`)
                    // 🚨 ИСПРАВЛЕНИЕ 2: Заменяем ВТОРОЙ '/0/' на /modelId/
                    .replace('/0/', `/${modelId}/`)
                    // 🚨 ИСПРАВЛЕНИЕ 3: Заменяем ТРЕТИЙ '/0/' на /generationId/
                    .replace('/0/', `/${generationId}/`);

                newAction = actionWithAllPks;
            }

        } else if (modelId) {
            // СЛУЧАЙ 2: Выбрана Модель -> СПИСОК ГЕНЕРАЦИЙ (2 PK)
            if (generationsListUrlTemplate) {
                let actionWithPk = generationsListUrlTemplate
                    // 🚨 ИСПРАВЛЕНИЕ 1: Заменяем ПЕРВЫЙ '/0/' на /makeId/
                    .replace('/0/', `/${makeId}/`)
                    // 🚨 ИСПРАВЛЕНИЕ 2: Заменяем ВТОРОЙ '/0/' на /modelId/
                    .replace('/0/', `/${modelId}/`);

                newAction = actionWithPk;
            }
        } else if (makeId) {
            // СЛУЧАЙ 1: Выбрана только Марка -> СПИСОК МОДЕЛЕЙ (1 PK)
            if (modelsListUrlTemplate) {
                 // 🚨 ИСПРАВЛЕНИЕ: Заменяем ПЕРВЫЙ '/0/' на /makeId/
                 newAction = modelsListUrlTemplate.replace('/0/', `/${makeId}/`);
            }
        }

        // Устанавливаем новый Action
        filterForm.setAttribute('action', newAction);

        // ЗАЩИТА ОТ "Cannot set properties of null"
        if (submitButton) {
            submitButton.disabled = false;
        }

        console.log(`[JS Debug] New Form Action (Final): ${newAction}`);
    }

    // =========================================================================
    // Принудительная отправка
    // =========================================================================

    if (submitButton) {
        submitButton.addEventListener('click', function(e) {
            e.preventDefault();

            if (this.disabled) {
                return;
            }

            console.warn(`[JS FINAL ACTION] Submitting to: ${filterForm.getAttribute('action')}`);

            filterForm.submit();
        });
    }

    // =========================================================================
    // ОБРАБОТЧИКИ СОБЫТИЙ
    // =========================================================================

    // 1. Изменение Марки
    makeSelect.addEventListener('change', function() {
        const makeId = this.value;

        // ЛОГ №1: Чтение значения из дропдауна
        console.log('[LOG 1: Event Listener] Считанное значение makeId:', makeId);

        // Очистка и блокировка полей
        modelSelect.innerHTML = '<option value="">-- Сначала выберите марку --</option>';
        generationSelect.innerHTML = '<option value="">-- Сначала выберите модель --</option>';
        modelSelect.disabled = true;
        generationSelect.disabled = true;

        if (makeId) {
            loadModels(makeId);
        }
        updateFormAction();
    });

    // 2. Изменение Модели
    modelSelect.addEventListener('change', function() {
        const modelId = this.value;
        generationSelect.innerHTML = '<option value="">-- Сначала выберите модель --</option>';
        generationSelect.disabled = true;

        if (modelId) {
            loadGenerations(modelId);
        }
        updateFormAction();
    });

    // --- 3. Обработка выбора ПОКОЛЕНИЯ (обновление action) ---
    generationSelect.addEventListener('change', updateFormAction);
    // Инициализация при загрузке страницы
    updateFormAction();
});