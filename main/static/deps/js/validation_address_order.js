$(document).ready(function () {
    // 1. Маска телефона
    $("#id_phone").mask("+7 (999) 999-99-99");

    // 2. Логика скрытия/показа адреса доставки
    var $deliveryCheckbox = $('#id_requires_delivery');
    var $addressContainer = $('#container-delivery_address');
    var $addressInput = $('#id_delivery_address');

    function toggleDeliveryAddress() {
        if ($deliveryCheckbox.is(':checked')) {
            $addressContainer.slideDown();
            $addressContainer.find('label').append('<span class="text-danger required-asterisk"> *</span>');
        } else {
            $addressContainer.slideUp();
            $addressContainer.find('.required-asterisk').remove();
            $addressInput.removeClass('is-invalid');
        }
    }

    toggleDeliveryAddress();
    $deliveryCheckbox.change(toggleDeliveryAddress);

    // 3. Обработка AJAX отправки формы
    $('#submit-order-btn').click(function() {
        var $form = $('#order-form-modal');
        var url = $form.attr('action');
        var data = $form.serialize();

        // Сброс ошибок перед отправкой
        $('.is-invalid').removeClass('is-invalid');
        $('.invalid-feedback').text('');
        $('#modal-global-errors').addClass('d-none').text('');

        $.ajax({
            type: "POST",
            url: url,
            data: data,
            success: function(response) {
                if (response.success) {

                    // 1. Закрываем модальное окно оформления заказа
                    $('#orderModal').modal('hide');

                    // 2. Удаляем старое модальное окно успеха, если оно вдруг есть (чтобы не дублировать)
                    $('#orderSuccessModal').remove();

                    // 3. Вставляем полученный HTML в конец body
                    $('body').append(response.modal_html);

                    // 4. Инициализируем и показываем новое модальное окно
                    var successModal = new bootstrap.Modal(document.getElementById('orderSuccessModal'));
                    successModal.show();

                    // 5. ОПЦИОНАЛЬНО: Когда пользователь закроет окно успеха или перейдет на главную,
                    // корзина на фоне должна обновиться (стать пустой).
                    // Самый простой способ - перезагрузить страницу при закрытии модалки:
                    var modalEl = document.getElementById('orderSuccessModal');
                    modalEl.addEventListener('hidden.bs.modal', function (event) {
                         window.location.reload(); // или window.location.href = "{% url 'index' %}";
                    });

                } else {
                    // Ошибки полей
                    if (response.errors) {
                        $.each(response.errors, function(field, messages) {
                            var $input = $('#id_' + field);
                            var $errorContainer = $('#error-' + field);
                            $input.addClass('is-invalid');
                            $errorContainer.text(messages[0]);
                        });
                    }
                    // Общая ошибка
                    if (response.error_message) {
                        $('#modal-global-errors').removeClass('d-none').text(response.error_message);
                    }
                }
            },
            error: function(xhr) {
                $('#modal-global-errors').removeClass('d-none').text('Ошибка соединения с сервером.');
            }
        });
    });
});