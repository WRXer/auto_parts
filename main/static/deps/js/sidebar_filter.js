// static/deps/js/sidebar_filter.js



function resetModelAndGeneration() {
    const modelSelect = document.getElementById('id_model_sidebar');
    const generationSelect = document.getElementById('id_generation_sidebar');

    if (modelSelect) {
        modelSelect.innerHTML = '<option value="">-- Все модели --</option>';
        modelSelect.disabled = true;
    }

    if (generationSelect) {
        generationSelect.innerHTML = '<option value="">-- Все модификации --</option>';
        generationSelect.disabled = true;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const makeSelect = document.getElementById('id_make_sidebar');
    const modelSelect = document.getElementById('id_model_sidebar');
    const generationSelect = document.getElementById('id_generation_sidebar');
    const filterForm = document.getElementById('sidebar-filter-form');
    if (!makeSelect || !modelSelect || !generationSelect || !filterForm) return;

    const hiddenGenerationInput = document.getElementById('initial_generation_id_hidden');
    const initialGenerationId = hiddenGenerationInput ? hiddenGenerationInput.value : generationSelect.value;
    const initialMakeId = makeSelect.value;
    const initialModelId = modelSelect.value;
    const loadModelsUrl = makeSelect.dataset.loadModelsUrl;
    const loadGenerationsUrl = makeSelect.dataset.loadGenerationsUrl;

    // === Заполнение select ===
    function populateSelect(select, data, defaultText, selectedId) {
        // 👇 Создаем фрагмент, не трогая текущий select до конца
        const fragment = document.createDocumentFragment();
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = `-- ${defaultText} --`;
        fragment.appendChild(defaultOption);

        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name;
            if (String(item.id) === String(selectedId)) {
                option.selected = true;
            }
            fragment.appendChild(option);
        });

        // 👇 Только теперь обновляем содержимое
        select.innerHTML = '';
        select.appendChild(fragment);
        select.disabled = data.length === 0;
    }

    // === AJAX ===
    async function loadModels(makeId, autoSubmit = false) {
        try {
            const res = await fetch(`${loadModelsUrl}?make_id=${makeId}`);
            const data = await res.json();
            populateSelect(modelSelect, data, 'Все модели', initialModelId);

            // Сбрасываем поколение только после полной загрузки моделей
            generationSelect.innerHTML = `<option value="">-- Все модификации --</option>`;
            generationSelect.disabled = true;

            if (autoSubmit) filterForm.submit();
        } catch (e) {
            console.error(e);
        }
    }

    async function loadGenerations(modelId, autoSubmit = false) {
        try {
            const res = await fetch(`${loadGenerationsUrl}?model_id=${modelId}`);
            const data = await res.json();

            // 💡 Если есть выбранное поколение — не показываем “все модификации” моргом

            populateSelect(generationSelect, data, 'Все модификации', initialGenerationId);

            if (autoSubmit) filterForm.submit();
        } catch (e) {
            console.error(e);
        }
    }

    // === Обработчики ===
    makeSelect.addEventListener('change', () => {
        const id = makeSelect.value;
        if (id) loadModels(id, true);
        else filterForm.submit();
    });

    modelSelect.addEventListener('change', () => {
        const id = modelSelect.value;
        if (id) loadGenerations(id, true);
        else filterForm.submit();
    });

    generationSelect.addEventListener('change', () => filterForm.submit());

    // === Инициализация ===
    if (initialMakeId && modelSelect.options.length <= 1) {
        loadModels(initialMakeId);
    }
    if (initialModelId && generationSelect.options.length <= 1) {
        loadGenerations(initialModelId);
    }
});

// Функция для сворачивания/разворачивания фильтра
    function toggleFilterBody() {
        const cardBody = document.querySelector('.card-body');
        const arrow = document.getElementById('filter-arrow');

        cardBody.classList.toggle('d-none'); // Временно используем d-none для простоты
        if (cardBody.classList.contains('d-none')) {
            arrow.classList.replace('bi-chevron-down', 'bi-chevron-right');
        } else {
            arrow.classList.replace('bi-chevron-right', 'bi-chevron-down');
        }
    }