document.addEventListener('DOMContentLoaded', function() {
    // 1. Идентификаторы
    const deliveryToggle = document.querySelector('.requires-delivery-toggle');
    const addressInput = document.getElementById('id_delivery_address');
    const addressAsterisk = document.querySelector('.required-asterisk-delivery_address');

    // Проверяем, что элементы существуют
    if (deliveryToggle && addressInput) {

        // Функция, которая обновляет состояние поля адреса (визуально и функционально)
        function toggleAddressRequirement() {
            const requiresDelivery = deliveryToggle.checked;

            if (requiresDelivery) {
                // Доставка требуется: делаем поле обязательным и показываем звездочку
                addressInput.setAttribute('required', 'required');
                if (addressAsterisk) {
                    addressAsterisk.style.display = 'inline';
                }
            } else {
                // Доставка не требуется: делаем поле необязательным и скрываем звездочку
                addressInput.removeAttribute('required');
                if (addressAsterisk) {
                    addressAsterisk.style.display = 'none';
                }
            }
        }

        // Устанавливаем начальное состояние при загрузке страницы
        toggleAddressRequirement();

        // Добавляем слушатель события change для динамического обновления
        deliveryToggle.addEventListener('change', toggleAddressRequirement);
    }
});
