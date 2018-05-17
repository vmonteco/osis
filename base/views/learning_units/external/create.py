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
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods

from attribution.business import attribution_charge_new
from base import models as mdl
from base.business.learning_unit import get_cms_label_data, \
    get_same_container_year_components, get_components_identification, get_organization_from_learning_unit_year, \
    get_campus_from_learning_unit_year, \
    get_all_attributions, find_language_in_settings, \
    CMS_LABEL_SPECIFICATIONS, get_achievements_group_by_language
from base.business.learning_unit_proposal import get_difference_of_proposal
from base.business.learning_units import perms as business_perms
from base.business.learning_units.perms import learning_unit_year_permissions, learning_unit_proposal_permissions, \
    can_update_learning_achievement
from base.forms.learning_class import LearningClassEditForm
from base.forms.learning_unit.learning_unit_create_2 import FullForm, ExternalForm, LearningUnitExternalBaseForm
from base.forms.learning_unit_component import LearningUnitComponentEditForm
from base.forms.learning_unit_pedagogy import LearningUnitPedagogyEditForm
from base.forms.learning_unit_specifications import LearningUnitSpecificationsForm, LearningUnitSpecificationsEditForm
from base.models import proposal_learning_unit, education_group_year
from base.models.academic_year import AcademicYear
from base.models.learning_unit import REGEX_BY_SUBTYPE
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views.learning_units import perms
from base.views.learning_units.common import show_success_learning_unit_year_creation_message
from cms.models import text_label
from osis_common.decorators.ajax import ajax_required
from base.views import layout
from base.forms.learning_unit.learning_unit_create_2 import CreationExternalBaseForm
from base.models.enums.learning_container_year_types import EXTERNAL
from base.forms.learning_unit.learning_unit_external import LearningUnitExternalForm

@login_required
@permission_required('base.can_propose_learningunit', raise_exception=True)
def get_external_learning_unit_creation_form(request, academic_year):
    print('get_external_learning_unit_creation_form')
    person = get_object_or_404(Person, user=request.user)
    academic_year = get_object_or_404(AcademicYear, pk=academic_year)
    if request.POST:
        print('post')
        external_form = CreationExternalBaseForm(request.POST or None, person, academic_year)

        if external_form.is_valid():
            print('is_valid')
            proposal = external_form.save()
            show_success_learning_unit_year_creation_message(request, proposal.learning_unit_year,
                                                             'proposal_learning_unit_successfuly_created')
            return redirect('learning_unit', learning_unit_year_id=proposal.learning_unit_year.pk)

        return layout.render(request, "learning_unit/simple/creation_external.html", external_form.get_context())
    else:
        print('get')
        # learning_unit_form_container = CreationExternalBaseForm(None, person,
        #                                         default_ac_year=get_object_or_404(AcademicYear, pk=academic_year.id))
        # learning_unit_form_container = LearningUnitExternalBaseForm()



        postponement_form = LearningUnitExternalForm(
            person=person,
            start_postponement=academic_year,
            data=request.POST or None
        )



        return layout.render(request, "learning_unit/simple/creation_external.html", learning_unit_form_container.get_context())





