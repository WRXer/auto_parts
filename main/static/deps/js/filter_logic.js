// static/js/filter_logic.js

document.addEventListener('DOMContentLoaded', function() {
    const makeSelect = document.getElementById('id_make');
    const modelSelect = document.getElementById('id_model');
    const generationSelect = document.getElementById('id_generation'); // Предполагается, что id='id_generation'
    const filterForm = document.getElementById('filter-form');         // 🌟 Получаем форму

    // Получаем URL-адреса из HTML-элемента
    const loadModelsUrl = makeSelect.dataset.loadModelsUrl;
    const loadGenerationsUrl = makeSelect.dataset.loadGenerationsUrl;

    // 🌟 НОВЫЕ URL ДЛЯ ДИНАМИЧЕСКОГО ACTION 🌟
    const carModelListUrl = makeSelect.dataset.carModelListUrl;
    const defaultAction = makeSelect.dataset.defaultAction;


    // --- Функция очистки и блокировки ---
    function resetModelAndGeneration(message) {
        modelSelect.innerHTML = `<option value="">${message}</option>`;
        modelSelect.disabled = true;
        generationSelect.innerHTML = `<option value="">Сначала выберите модель</option>`;
        generationSelect.disabled = true;
    }

    // --- Функция обновления ACTION формы ---
    function updateFormAction(makeId, modelId, generationId) {
        if (makeId && !modelId && !generationId) {
            // Если выбрана только Марка, меняем action на список моделей
            // Заменяем фиктивный '0' на реальный makeId в URL
            const newAction = carModelListUrl.replace('/0/', `/${makeId}/`);
            filterForm.setAttribute('action', newAction);
        } else {
            // Если выбрана Модель или Модификация, или ничего не выбрано,
            // используем действие по умолчанию (all_parts)
            filterForm.setAttribute('action', defaultAction);
        }
        filterForm.setAttribute('method', 'GET'); // Метод всегда GET
    }

    // --- 1. Обработка выбора МАРКИ (Загрузка Моделей и обновление action) ---
    makeSelect.addEventListener('change', function() {
        const makeId = this.value;
        const modelId = modelSelect.value;
        const generationId = generationSelect.value;

        resetModelAndGeneration('Загрузка моделей...');
        updateFormAction(makeId, modelId, generationId); // 🌟 Обновляем action при выборе марки

        if (makeId) {
            const url = loadModelsUrl + '?make_id=' + makeId;

            fetch(url)
                .then(response => response.json())
                .then(models => {
                    modelSelect.innerHTML = '<option value="">-- Выберите модель --</option>';
                    modelSelect.disabled = (models.length === 0);

                    if (models.length === 0) {
                         modelSelect.innerHTML = '<option value="">-- Модели не найдены --</option>';
                    } else {
                        models.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model.id;
                            option.textContent = model.name;
                            modelSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Ошибка при загрузке моделей:', error);
                    resetModelAndGeneration('Ошибка загрузки');
                });
        } else {
            resetModelAndGeneration('-- Сначала выберите марку --');
        }
    });

    // --- 2. Обработка выбора МОДЕЛИ (Загрузка Поколений и обновление action) ---
    modelSelect.addEventListener('change', function() {
        const modelId = this.value;
        const makeId = makeSelect.value;
        const generationId = generationSelect.value;

        // 🌟 Обновляем action при выборе модели (снова на all_parts, если модель выбрана)
        updateFormAction(makeId, modelId, generationId);

        generationSelect.innerHTML = '<option value="">Загрузка модификаций...</option>';
        generationSelect.disabled = true;

        if (modelId) {
            const url = loadGenerationsUrl + '?model_id=' + modelId;

            fetch(url)
                .then(response => response.json())
                .then(generations => {
                    generationSelect.innerHTML = '<option value="">-- Выберите модификацию --</option>';
                    generationSelect.disabled = (generations.length === 0);

                    if (generations.length === 0) {
                         generationSelect.innerHTML = '<option value="">-- Модификации не найдены --</option>';
                    } else {
                        generations.forEach(mod => {
                            const option = document.createElement('option');
                            option.value = mod.id;
                            option.textContent = mod.name;
                            generationSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Ошибка при загрузке модификаций:', error);
                    generationSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
                });
        } else {
            generationSelect.innerHTML = '<option value="">-- Сначала выберите модель --</option>';
        }
    });

    // --- 3. Обработка выбора ПОКОЛЕНИЯ (обновление action) ---
    generationSelect.addEventListener('change', function() {
        const makeId = makeSelect.value;
        const modelId = modelSelect.value;
        const generationId = this.value;

        // 🌟 Обновляем action при выборе поколения (снова на all_parts)
        updateFormAction(makeId, modelId, generationId);
    });
});