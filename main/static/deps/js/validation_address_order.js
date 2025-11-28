$(document).ready(function() {

    const $phoneInput = $("#id_phone");

    // =================================================================
    // Функция для предварительной обработки значения телефона
    // Удаляет 8 или 7 в начале, если номер состоит из 11 цифр.
    // =================================================================
    function preprocessPhoneValue(value) {
        // 1. Удаляем все не-цифры (оставляем только цифры)
        let digits = value.replace(/\D/g, '');

        // 2. Если номер начинается с '8' или '7' и состоит из 11 цифр (полный российский формат)
        if (digits.length === 11 && (digits.startsWith('8') || digits.startsWith('7'))) {
            // Удаляем первую цифру (8 или 7) -> оставляем 10 цифр
            return digits.substring(1);
        }

        // 3. В остальных случаях возвращаем все цифры, как есть (например, 10 цифр или короткий ввод)
        return digits;
    }


    // =================================================================
    // 1. Применяем маску к полю телефона
    // =================================================================

    // Получаем текущее значение поля (от Django/Autofill)
    let initialValue = $phoneInput.val();

    // ПРЕДВАРИТЕЛЬНО обрабатываем и устанавливаем только 10 цифр
    let cleanedInitialValue = preprocessPhoneValue(initialValue);
    $phoneInput.val(cleanedInitialValue);

    // Применяем маску к полю. Теперь маска видит только 10 цифр и добавляет +7
    $phoneInput.mask("+7 (999) 999-99-99");


    // Дополнительный обработчик на событие 'blur' (уход фокуса)
    // Это ловит случаи, когда пользователь вставляет '8927...' или Autofill "засовывает" 8/7.
    $phoneInput.on('blur', function() {
        let currentValue = $phoneInput.val();
        let cleanedValue = preprocessPhoneValue(currentValue);

        // Сравниваем длину полученных цифр с очищенным значением.
        // Если длина изменилась (т.е. была удалена ведущая 8 или 7),
        // принудительно снимаем маску, устанавливаем очищенное значение и применяем маску снова.
        if (cleanedValue.length !== currentValue.replace(/\D/g, '').length) {
            $phoneInput.unmask().val(cleanedValue).mask("+7 (999) 999-99-99");
        }
    });


    // =================================================================
    // 2. Логика отображения/скрытия поля адреса
    // =================================================================
    const $requiresDelivery = $('#id_requires_delivery');
    const $deliveryAddressContainer = $('div[data-field-name="delivery_address"]');
    const $deliveryAddressInput = $('#id_delivery_address');
    const $deliveryAddressAsterisk = $('.required-asterisk-delivery_address');

    /**
     * Переключает видимость поля адреса доставки и его обязательность (required).
     */
    function toggleAddressField() {
        if ($requiresDelivery.is(':checked')) {
            // Доставка требуется: показываем поле и делаем его обязательным
            $deliveryAddressContainer.slideDown(200);
            $deliveryAddressAsterisk.show();
            $deliveryAddressInput.prop('required', true);
        } else {
            // Доставка не требуется: скрываем поле и убираем обязательность
            $deliveryAddressContainer.slideUp(200);
            $deliveryAddressAsterisk.hide();
            $deliveryAddressInput.prop('required', false);
            // Убираем потенциальное выделение ошибки
            $deliveryAddressInput.removeClass('is-invalid');
        }
    }

    // Инициализация при загрузке
    if (!$requiresDelivery.is(':checked')) {
        $deliveryAddressInput.prop('required', false);
    }

    $requiresDelivery.on('change', function() {
        toggleAddressField();
    });
});