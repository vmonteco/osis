let formAjaxSubmit = function (form, modal) {
    $(form).submit(function (e) {
        // Added preventDefaut so as to not add anchor "href" to address bar
        e.preventDefault();

        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr, ajaxOptions, thrownError) {
                if ($(xhr).find('.has-error').length > 0) {
                    $(modal).find('.modal-content').html(xhr);
                    formAjaxSubmit(form, modal);
                } else {
                    $(modal).modal('toggle');
                    if (xhr.hasOwnProperty('success_url')) {
                        window.location.href = xhr["success_url"];
                    }
                    else {
                        window.location.reload();
                    }
                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                // handle response errors here
            }
        });
    });
};
