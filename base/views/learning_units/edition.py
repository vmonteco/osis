##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.forms.models import model_to_dict

from base.models import entity_container_year
from base.views.learning_unit import get_learning_unit_identification_context
from base.business.learning_units.edition import edit_learning_unit_end_date
from base.forms.learning_unit.edition import LearningUnitEndDateForm, LearningUnitModificationForm
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views import layout
from base.views.common import display_error_messages, display_success_messages
from base.views.learning_units import perms


@login_required
@permission_required('base.can_edit_learningunit_date', raise_exception=True)
@perms.can_perform_end_date_modification
def learning_unit_edition(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    user_person = get_object_or_404(Person, user=request.user)

    context = get_learning_unit_identification_context(learning_unit_year_id, user_person)

    learning_unit_to_edit = learning_unit_year.learning_unit
    form = LearningUnitEndDateForm(request.POST or None, learning_unit=learning_unit_to_edit)
    if form.is_valid():
        new_academic_year = form.cleaned_data['academic_year']
        try:
            result = edit_learning_unit_end_date(learning_unit_to_edit, new_academic_year)
            display_success_messages(request, result)

            learning_unit_year_id = _get_current_learning_unit_year_id(learning_unit_to_edit, learning_unit_year_id)

            return HttpResponseRedirect(reverse('learning_unit', args=[learning_unit_year_id]))

        except IntegrityError as e:
            display_error_messages(request, e.args[0])

    context['form'] = form
    return layout.render(request, 'learning_unit/edition.html', context)


@login_required
@permission_required('base.can_edit_learningunit', raise_exception=True)
@perms.can_perform_learning_unit_modification
def modify_learning_unit(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    initial_data = compute_form_initial_data(learning_unit_year)
    form = LearningUnitModificationForm(initial=initial_data)

    context = {
        "learning_unit_year": learning_unit_year,
        "form": form
    }
    return layout.render(request, 'learning_unit/modification.html', context)


def compute_form_initial_data(learning_unit_year):
    learning_unit_year_fields_to_exclude = ["external_id", "changed", "id", "acronym", "learning_container_year",
                                            "learning_unit", "specific_title", "specific_title_english",
                                            "structure", "decimal_scores"]
    learning_container_year_fields_to_exclude = ["external_id", "changed", "id", "academic_year", "learning_container",
                                                 "in_charge", "acronym"]
    learning_unit_fields_to_include = ["faculty_remark", "other_remark", "periodicity"]
    learning_unit_year_key_values = model_to_dict(learning_unit_year, exclude=learning_unit_year_fields_to_exclude)
    learning_container_year_key_values = model_to_dict(learning_unit_year.learning_container_year,
                                                       exclude=learning_container_year_fields_to_exclude)
    learning_unit_keys_values = model_to_dict(learning_unit_year.learning_unit, fields=learning_unit_fields_to_include)
    other_fields = {
        "partial_title": learning_unit_year.specific_title,
        "partial_english_title": learning_unit_year.specific_title_english,
        "first_letter": learning_unit_year.acronym[0],
        "acronym": learning_unit_year.acronym[1:]
    }
    initial_data = dict()
    initial_data.update(learning_unit_year_key_values)
    initial_data.update(learning_container_year_key_values)
    initial_data.update(learning_unit_keys_values)
    initial_data.update(other_fields)

    attributions = entity_container_year.find_last_entity_version_grouped_by_linktypes(
        learning_unit_year.learning_container_year
    )
    initial_data.update({k.lower(): v.id for k, v in attributions.items()})

    return {key: value for key, value in initial_data.items() if value is not None}



def _get_current_learning_unit_year_id(learning_unit_to_edit, learning_unit_year_id):
    if not LearningUnitYear.objects.filter(pk=learning_unit_year_id).exists():
        result = LearningUnitYear.objects.filter(learning_unit=learning_unit_to_edit).last().pk
    else:
        result = learning_unit_year_id
    return result
