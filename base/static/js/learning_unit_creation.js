const internship = "INTERNSHIP";
    var form = $('#LearningUnitYearForm').closest("form");

    function showInternshipSubtype(){
        var container_type_value = document.getElementById('id_container_type').value;
        document.getElementById('id_internship_subtype').disabled = container_type_value != internship;
    }

    function showAdditionalEntity(elem, id){
        document.getElementById(id).disabled = elem == "";
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
                            $('#acronym_message').addClass("error").text(trans_existed_acronym);
                            $("#acronym_message").css("color","red");
                            window.acronym_already_used = true;
                        }
                    }
                });
            } else {
                window.valid_acronym = false;
                $('#acronym_message').addClass("error").text(trans_invalid_acronym);
                $("#acronym_message").css("color","red");
            }
        }
    };

    function setFirstLetter(){
        var url = "?campus=" + $('#id_campus').val()
        $.ajax({
            url: form.attr("code-validate-url")+url
        }).done(function(data){
            document.getElementById('id_first_letter').value = data['code'];
            validate_acronym();
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
        document.getElementById('id_additional_entity_1').disabled = '{{form.requirement_entity.value}}' != "0";
        document.getElementById('id_additional_entity_2').disabled = '{{form.requirement_entity_1.value}}' != "0";

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