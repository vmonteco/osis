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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.http import QueryDict, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base import models as mdl
from base.business.learning_unit_proposal import compute_proposal_type, reinitialize_data_before_proposal, \
    delete_learning_unit_proposal
from base.forms.common import TooManyResultsException
from base.forms.learning_unit_proposal import LearningUnitProposalModificationForm
from base.forms.proposal.learning_unit_proposal import LearningUnitProposalForm, ProposalStateModelForm
from base.models import proposal_learning_unit
from base.models.enums import proposal_state
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.models.proposal_learning_unit import ProposalLearningUnit
from base.views import layout
from base.views.common import display_success_messages, display_error_messages
from base.views.learning_unit import check_if_display_message
from base.views.learning_unit import compute_form_initial_data, get_learning_unit_identification_context
from base.views.learning_unit import get_last_academic_years
from base.views.learning_units import perms

PROPOSAL_SEARCH = 3


@login_required
@perms.can_create_modification_proposal
@permission_required('base.can_propose_learningunit', raise_exception=True)
def propose_modification_of_learning_unit(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, id=learning_unit_year_id)
    user_person = get_object_or_404(Person, user=request.user)
    initial_data = compute_form_initial_data(learning_unit_year)

    if request.method == 'POST':
        modified_post_data = request.POST.copy()
        post_data_merged = QueryDict('', mutable=True)
        post_data_merged.update(initial_data)
        post_data_merged.update(modified_post_data)

        form = LearningUnitProposalModificationForm(post_data_merged, initial=initial_data)
        if form.is_valid():
            type_proposal = compute_proposal_type(initial_data, modified_post_data)
            form.save(learning_unit_year, user_person, type_proposal, proposal_state.ProposalState.FACULTY.name)
            messages.add_message(request, messages.SUCCESS,
                                 _("success_modification_proposal")
                                 .format(_(type_proposal), learning_unit_year.acronym))
            return redirect('learning_unit', learning_unit_year_id=learning_unit_year.id)
    else:
        form = LearningUnitProposalModificationForm(initial=initial_data)

    return render(request, 'learning_unit/proposal/update.html', {
        'learning_unit_year': learning_unit_year,
        'person': user_person,
        'form': form,
        'experimental_phase': True})


@login_required
@perms.can_perform_cancel_proposal
@permission_required('base.can_propose_learningunit', raise_exception=True)
def cancel_proposal_of_learning_unit(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, id=learning_unit_year_id)
    learning_unit_proposal = get_object_or_404(ProposalLearningUnit, learning_unit_year=learning_unit_year)
    reinitialize_data_before_proposal(learning_unit_proposal, learning_unit_year)
    delete_learning_unit_proposal(learning_unit_proposal)
    messages.add_message(request, messages.SUCCESS,
                         _("success_cancel_proposal").format(learning_unit_year.acronym))
    return redirect('learning_unit', learning_unit_year_id=learning_unit_year.id)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units_proposal_search(request):
    form = LearningUnitProposalForm(request.GET or None)
    found_learning_units = []
    proposals = []
    try:
        if form.is_valid():
            data = form._get_proposal_learning_units()
            found_learning_units = data.get('learning_units')
            proposals = data.get('proposals')
            check_if_display_message(request, proposals)
    except TooManyResultsException:
        messages.add_message(request, messages.ERROR, _('too_many_results'))

    context = {
        'form': form,
        'academic_years': get_last_academic_years(),
        'current_academic_year': mdl.academic_year.current_academic_year(),
        'experimental_phase': True,
        'search_type': PROPOSAL_SEARCH,
        'proposals': proposals,
        'learning_units': found_learning_units
    }

    return layout.render(request, "learning_units.html", context)


@login_required
@permission_required('base.can_edit_learningunit', raise_exception=True)
@perms.can_edit_learning_unit_proposal
def edit_proposal(request, learning_unit_year_id):
    user_person = get_object_or_404(Person, user=request.user)

    context = get_learning_unit_identification_context(learning_unit_year_id, user_person)
    proposal = proposal_learning_unit.find_by_learning_unit_year(learning_unit_year_id)

    proposal_form = ProposalStateModelForm(request.POST or None, instance=proposal)
    if request.POST:
        try:
            proposal_form.save()
            display_success_messages(request, _("Proposal edited successfully"))
            return HttpResponseRedirect(reverse('learning_unit', args=[learning_unit_year_id]))

        except (IntegrityError, ValueError) as e:
            display_error_messages(request, e.args[0])

    context['form'] = proposal_form
    return layout.render(request, 'learning_unit/proposal/edition_proposal_state.html', context)
