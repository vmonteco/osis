function redirect_after_success(modal, xhr) {
    $(modal).modal('toggle');
    if (xhr.hasOwnProperty('success_url')) {
        window.location.href = xhr["success_url"];
    }
    else {
        window.location.reload();
    }
}

var formAjaxSubmit = function (form, modal) {
    $(form).submit(function (e) {
        // Added preventDefaut so as to not add anchor "href" to address bar
        e.preventDefault();

        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr, ajaxOptions, thrownError) {

                //Stay on the form if there are errors.
                if ($(xhr).find('.has-error').length > 0) {
                    $(modal).find('.modal-content').html(xhr);
                    formAjaxSubmit(form, modal);
                } else {
                    redirect_after_success(modal, xhr);
                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                // handle response errors here
            }
        });
    });
};
