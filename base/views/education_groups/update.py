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
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from waffle.decorators import waffle_flag

from base.business.learning_unit_proposal import compute_proposal_state
from base.forms.learning_unit.edition import LearningUnitEndDateForm
from base.forms.learning_unit_proposal import ProposalLearningUnitForm, ProposalBaseForm
from base.models.enums.proposal_type import ProposalType
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.models.proposal_learning_unit import ProposalLearningUnit
from base.views import layout
from base.views.common import display_success_messages
from base.views.learning_units import perms
from base.views.learning_units.common import get_learning_unit_identification_context
from base.forms.education_group.edition import EditionEducationGroupYearForm, EducationGroupForm, \
    EducationGroupTypeForm, UpdateOfferYearManagementEntityForm
from base.models.education_group_year import EducationGroupYear
from base.forms.education_group.create import CreateOfferYearEntityForm
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from base.models.enums import education_group_categories
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _

from base.forms.education_group.create import CreateEducationGroupYearForm, CreateOfferYearEntityForm
from base.models.education_group_year import EducationGroupYear
from base.models.enums import offer_year_entity_type
from base.models.offer_year_entity import OfferYearEntity
from base.views import layout
from base.views.common import display_success_messages, reverse_url_with_query_string
from base.views.education_groups.perms import can_change_education_group


@login_required
@user_passes_test(can_change_education_group)
def update_education_group(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    root = request.GET.get("root")

    offer_year_entity = get_object_or_404(
        OfferYearEntity, education_group_year=education_group_year, type=offer_year_entity_type.ENTITY_ADMINISTRATION
    )

    if education_group_year.education_group_type.category == education_group_categories.GROUP:
        form_education_group_year = CreateEducationGroupYearForm(request.POST or None, instance=education_group_year)
    elif education_group_year.education_group_type.category == education_group_categories.TRAINING:
        form_education_group_year = EditionEducationGroupYearForm(request.POST or None, instance=education_group_year)

    form_offer_year_entity = CreateOfferYearEntityForm(request.POST or None, instance=offer_year_entity)

    if form_offer_year_entity.is_valid() and form_education_group_year.is_valid():
        education_group_year = form_education_group_year.save()
        form_offer_year_entity.save(education_group_year)

        display_success_messages(request, _("Education group successfully updated"))
        url = reverse_url_with_query_string("education_group_read",
                                            args=[education_group_year.id],
                                            query={"root": root})
        return redirect(url)

    return layout.render(request, "education_group/update.html", {
        "form_education_group_year": form_education_group_year,
        "form_offer_year_entity": form_offer_year_entity,
        "education_group_year": education_group_year,
    })


@login_required
def identification_edit(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, id=education_group_year_id)

    if request.POST:
        form = EditionEducationGroupYearForm(request.POST or None, instance=education_group_year)
        if form.is_valid():
            print('valid')
            result = form.save()
            print(result)
            # display_success_messages(request, result, extra_tags='safe')
            return HttpResponseRedirect(reverse('education_group_read', args=[result.id]))

    else:
        form = EditionEducationGroupYearForm(instance=education_group_year)

    form_administrative_entity = CreateOfferYearEntityForm(initial={'entity': education_group_year.administration_entity})
    form_management_entity = UpdateOfferYearManagementEntityForm(initial={'entity': education_group_year.management_entity})
    form_education_group = EducationGroupForm(instance=education_group_year.education_group)
    form_education_group_type = EducationGroupTypeForm(instance=education_group_year.education_group_type)

    return layout.render(request, "education_group/identification_training_edit.html",
                         {'education_group_year': education_group_year,
                          'form': form,
                          'form_administrative_entity': form_administrative_entity,
                          'form_management_entity': form_management_entity,
                          'form_education_group': form_education_group,
                          'form_education_group_type': form_education_group_type})
