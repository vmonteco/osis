##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.models.academic_year import current_academic_year
from base.models.entity_container_year import find_last_entity_version_grouped_by_linktypes
from base.models.enums import entity_container_year_link_type, learning_unit_year_subtypes, proposal_type, \
    proposal_state
from base.forms.learning_unit_proposal import LearningUnitProposalModificationForm
from base.models import proposal_learning_unit


@login_required
def propose_modification_of_learning_unit(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, id=learning_unit_year_id)
    user_person = get_object_or_404(Person, user=request.user)
    proposal = proposal_learning_unit.find_by_learning_unit_year(learning_unit_year)
    current_year = current_academic_year().year

    if learning_unit_year.academic_year.year < current_year:
        messages.add_message(request, messages.ERROR, _("cannot_do_modification_proposal_for_past_learning_unit"))
        return redirect('learning_unit', learning_unit_year_id=learning_unit_year.id)

    if learning_unit_year.subtype != learning_unit_year_subtypes.FULL:
        messages.add_message(request, messages.ERROR, _("learning_unit_is_not_of_type_full"))
        return redirect('learning_unit', learning_unit_year_id=learning_unit_year.id)

    if proposal:
        messages.add_message(request, messages.ERROR, _("proposal_already_exists"))
        return redirect('learning_unit', learning_unit_year_id=learning_unit_year.id)

    entities_version = find_last_entity_version_grouped_by_linktypes(learning_unit_year.learning_container_year)
    initial_data = {
        "academic_year": learning_unit_year.academic_year.id,
        "first_letter": learning_unit_year.acronym[0],
        "acronym": learning_unit_year.acronym[1:],
        "title": learning_unit_year.title,
        "title_english": learning_unit_year.title_english,
        "learning_container_year_type": learning_unit_year.learning_container_year.container_type,
        "subtype": learning_unit_year.subtype,
        "internship_subtype": learning_unit_year.internship_subtype,
        "credits": float(learning_unit_year.credits),
        "periodicity": learning_unit_year.learning_unit.periodicity,
        "status": learning_unit_year.status,
        "language": learning_unit_year.learning_container_year.language,
        "quadrimester": learning_unit_year.quadrimester,
        "campus": learning_unit_year.learning_container_year.campus,
        "requirement_entity": entities_version.get(entity_container_year_link_type.REQUIREMENT_ENTITY),
        "allocation_entity": entities_version.get(entity_container_year_link_type.ALLOCATION_ENTITY),
        "additional_entity_1": entities_version.get(entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1),
        "additional_entity_2": entities_version.get(entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2)
    }

    if request.method == 'POST':
        form = LearningUnitProposalModificationForm(request.POST, initial=initial_data)
        if form.is_valid():
            type_proposal = compute_proposal_type(form.initial, form.cleaned_data)
            form.save(learning_unit_year, user_person, type_proposal, proposal_state.ProposalState.FACULTY.name)
            return redirect('learning_unit', learning_unit_year_id=learning_unit_year.id)
    else:
        form = LearningUnitProposalModificationForm(initial=initial_data)

    return render(request, 'proposal/learning_unit_modification.html', {'learning_unit_year': learning_unit_year,
                                                                        'person': user_person,
                                                                        'form': form,
                                                                        'experimental_phase': True})


def compute_proposal_type(initial_data, current_data):
    data_changed = compute_data_changed(initial_data, current_data)
    filtered_data_changed = filter(lambda key: key not in ["academic_year", "subtype", "acronym"], data_changed)
    transformation = current_data["acronym"] != "{}{}".format(initial_data["first_letter"], initial_data["acronym"])
    modification = any(map(lambda x: x != "acronym", filtered_data_changed))
    if transformation and modification:
        return proposal_type.ProposalType.TRANSFORMATION_AND_MODIFICATION.name
    elif transformation:
        return proposal_type.ProposalType.TRANSFORMATION.name
    return proposal_type.ProposalType.MODIFICATION.name


def compute_data_changed(initial_data, current_data):
    data_changed = []
    for key, value in initial_data.items():
        current_value = current_data.get(key)
        if str(value) != str(current_value):
            data_changed.append(key)
    return data_changed

