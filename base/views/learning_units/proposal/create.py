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
from django.db.models import BLANK_CHOICE_DASH
from django.shortcuts import redirect, get_object_or_404

from base import models as mdl_base
from base.business.learning_units.proposal import creation
from base.business.learning_units.proposal.common import compute_proposal_state
from base.forms.learning_unit_proposal import ProposalBaseForm
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.proposal_type import ProposalType
from base.views import layout
from base.views.learning_units.common import show_success_learning_unit_year_creation_message
from reference.models.language import find_by_code


@login_required
@permission_required('base.can_propose_learningunit', raise_exception=True)
def get_proposal_learning_unit_creation_form(request, academic_year):
    person = get_object_or_404(mdl_base.person.Person, user=request.user)
    proposal_form = ProposalBaseForm(request.POST or None, person, None, proposal_type=ProposalType.CREATION.name, default_ac_year=academic_year)

    if proposal_form.is_valid():
        proposal_form.save()

    return layout.render(request, "learning_unit/proposal/creation.html", proposal_form.get_context())


# FIXME Remove this duplicated method
@login_required
@permission_required('base.can_propose_learningunit', raise_exception=True)
def proposal_learning_unit_add(request):
    person = get_object_or_404(mdl_base.person.Person, user=request.user)
    learning_unit_form = LearningUnitProposalCreationForm(person, request.POST)
    proposal_form = LearningUnitProposalForm(request.POST)
    if learning_unit_form.is_valid() and proposal_form.is_valid():
        data_learning_unit = learning_unit_form.cleaned_data
        year = data_learning_unit['academic_year'].year
        new_learning_container = mdl_base.learning_container.LearningContainer.objects.create()
        new_learning_unit = create_learning_unit(data_learning_unit, new_learning_container, year)
        academic_year = mdl_base.academic_year.find_academic_year_by_year(year)
        new_learning_unit_year = create_learning_unit_year_structure(data_learning_unit, new_learning_container,
                                                                     new_learning_unit, academic_year)
        data_proposal = proposal_form.cleaned_data
        _proposal_create(data_proposal, new_learning_unit_year, person)
        show_success_learning_unit_year_creation_message(request, new_learning_unit_year,
                                                         'proposal_learning_unit_successfuly_created')
        return redirect('learning_unit', learning_unit_year_id=new_learning_unit_year.id)

    return layout.render(request, "learning_unit/proposal/creation.html",
                         {'learning_unit_form': learning_unit_form,
                          'proposal_form': proposal_form,
                          'person': person})


def _proposal_create(data_proposal, new_learning_unit_year, person):
    creation.create_learning_unit_proposal({'person': person,
                                            'folder_entity': data_proposal['entity'],
                                            'folder_id': data_proposal['folder_id'],
                                            'learning_unit_year': new_learning_unit_year,
                                            'state_proposal': compute_proposal_state(person),
                                            'type_proposal': ProposalType.CREATION.name,
                                            'initial_data': {}})
