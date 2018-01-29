const internship = "INTERNSHIP";
const LEARNING_UNIT_FULL_SUBTYPE = "FULL";

var form = $('#LearningUnitYearForm').closest("form");


function isLearningUnitSubtypeFull(){
    return document.getElementById('id_subtype').value == LEARNING_UNIT_FULL_SUBTYPE
}


function isValueEmpty(html_id){
    return document.getElementById(html_id).value == ""
}


function showInternshipSubtype(){
    if (isLearningUnitSubtypeFull()) {
        var container_type_value = document.getElementById('id_container_type').value;
        var value_not_internship = container_type_value != internship;
        if(document.getElementById('id_internship_subtype')){
            document.getElementById('id_internship_subtype').disabled = value_not_internship;
        }
        if (value_not_internship){
            $('#id_internship_subtype')[0].selectedIndex = 0;
        }
    }
}

    function updateAdditionalEntityEditability(elem, id, disable_only){
        var empty_element = elem == "";
        if (empty_element){
            $('#'.concat(id))[0].selectedIndex = 0;
            document.getElementById(id).disabled = true;
        }
        else if (!disable_only){
            document.getElementById(id).disabled = false;
        }
    }

    function validate_acronym () {
        $('#acronym_message').removeClass("error-message").text("");
        if($('#id_first_letter').val()!=""){
            window.valid_acronym = false;
            window.acronym_already_used = false;
            var newAcronym = $('#id_first_letter').val().toUpperCase()+$('#id_acronym').val().toUpperCase();
            if(currentAcronym && newAcronym === currentAcronym){
                window.valid_acronym = true;
            }

            else if(form_acronym_regex.test(newAcronym)) {
                var url = "?acronym=" + $('#id_first_letter').val() + $('#id_acronym').val() + "&year_id=" + $('#id_academic_year').val()
                $.ajax({
                    url: form.attr("data-validate-url")+url
                }).done(function(data){
                    if (data['valid']){
                        window.valid_acronym = true;
                        if(data['existed_acronym'] && !data['existing_acronym']){
                            $('#acronym_message').addClass("error").text(trans_existed_acronym+data['last_using']);
                            $("#acronym_message").css("color","orange");
                            window.acronym_already_used = true;
                        }
                    }else{
                        window.valid_acronym = false;
                        if(data['existing_acronym']){
                            set_error_message(trans_existing_acronym, '#acronym_message' );
                            window.acronym_already_used = true;
                        }
                    }
                });
            } else {
                window.valid_acronym = false;
                set_error_message(trans_invalid_acronym, '#acronym_message' )
            }
        }
    };

    function set_error_message(text, element){
        $(element).addClass("error").text(text);
        $(element).css("color","red");
    }

    function checkPartimLetter() {
        $('#partim_letter_message').removeClass("error-message").text("");
        partim_letter = $('#hdn_partim_letter').val();
        submit_btn = $('#learning_unit_year_add');
        submit_btn.prop('disabled', false);

        if (partim_letter && partim_letter != '') {
            acronym = $('#id_first_letter').val() + $('#id_acronym').val() + partim_letter;
            validateion_url = $('#LearningUnitYearForm').data('validate-url');
            year_id = $('#id_academic_year').val();

            validateAcronymAjax(validateion_url, acronym, year_id, function(data){
                if (data['existing_acronym']) {
                    set_error_message(trans_invalid_partim_letter, "#partim_letter_message"); //Show error message
                    submit_btn.prop('disabled', true);   //Disable button
                } else {
                    submit_btn.prop('disabled', false);  //Enable button
                }
            });
        }
    }

    function validateAcronymAjax(url, acronym, year_id, callback) {
        /**
        * This function will check if the acronym exist or have already existed
        **/
        queryString = "?acronym=" + acronym + "&year_id=" + year_id;
        $.ajax({
           url: url + queryString
        }).done(function(data){
            callback(data);
        });
    }

    $(document).ready(function() {
        $(function () {
            $('#LearningUnitYearForm').validate();
        });
        $.extend($.validator.messages, {
            required: trans_field_required
        });

        showInternshipSubtype();
        document.getElementById('id_additional_requirement_entity_1').disabled = !isLearningUnitSubtypeFull() || isValueEmpty('id_requirement_entity');
        document.getElementById('id_additional_requirement_entity_2').disabled = !isLearningUnitSubtypeFull() || isValueEmpty('id_additional_requirement_entity_1');


        $('#id_acronym').change(validate_acronym);
        $('#id_academic_year').change(validate_acronym);
        $("#LearningUnitYearForm").submit(function( event ) {
            if (!window.valid_acronym) {
                $("#id_acronym").focus();
            }
            return window.valid_acronym;
        });

        $('#learning_unit_year_add').click(function() {
            if(window.acronym_already_used){
                $form = $("#LearningUnitYearForm")
                $form.validate();
                var formIsValid = $form.valid();
                if(formIsValid){
                  $("#prolongOrCreateModal").modal();
                }
            } else {
                $("#LearningUnitYearForm").submit();
            }
        });
    });