document.addEventListener('DOMContentLoaded', function() {
    const makeSelect = document.getElementById('id_make');
    const modelSelect = document.getElementById('id_model');
    const modificationSelect = document.getElementById('id_modification');

    // Получаем URL-адреса из HTML-элемента (Шаг 3)
    const baseUrl = makeSelect.dataset.baseUrl;
    const loadModelsUrl = makeSelect.dataset.loadModelsUrl;
    const loadModificationsUrl = makeSelect.dataset.loadModificationsUrl;


    // --- Функция очистки и блокировки ---
    function resetModelAndModification(message) {
        modelSelect.innerHTML = `<option value="">${message}</option>`;
        modelSelect.disabled = true;
        modificationSelect.innerHTML = `<option value="">Сначала выберите модель</option>`;
        modificationSelect.disabled = true;
    }

    // --- 1. Обработка выбора МАРКИ (Загрузка Моделей) ---
    makeSelect.addEventListener('change', function() {
        const makeId = this.value;
        resetModelAndModification('Загрузка моделей...');

        if (makeId) {
            // Используем переданный URL
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
                    resetModelAndModification('Ошибка загрузки');
                });
        } else {
            resetModelAndModification('-- Сначала выберите марку --');
        }
    });

    // --- 2. Обработка выбора МОДЕЛИ (Загрузка Модификаций) ---
    modelSelect.addEventListener('change', function() {
        const modelId = this.value;

        modificationSelect.innerHTML = '<option value="">Загрузка модификаций...</option>';
        modificationSelect.disabled = true;

        if (modelId) {
            // Используем переданный URL
            const url = loadModificationsUrl + '?model_id=' + modelId;

            fetch(url)
                .then(response => response.json())
                .then(modifications => {
                    modificationSelect.innerHTML = '<option value="">-- Выберите модификацию --</option>';
                    modificationSelect.disabled = (modifications.length === 0);

                    if (modifications.length === 0) {
                         modificationSelect.innerHTML = '<option value="">-- Модификации не найдены --</option>';
                    } else {
                        modifications.forEach(mod => {
                            const option = document.createElement('option');
                            option.value = mod.id;
                            option.textContent = mod.name;
                            modificationSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Ошибка при загрузке модификаций:', error);
                    modificationSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
                });
        } else {
            modificationSelect.innerHTML = '<option value="">-- Сначала выберите модель --</option>';
        }
    });
});