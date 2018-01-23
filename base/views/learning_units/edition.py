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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from base.business.learning_units.edition import is_eligible_for_modification_end_date
from base.forms.learning_unit.edition import LearningUnitEndDateForm
from base.models import learning_unit_year as learning_unit_year_mdl
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views import layout
from base.views.learning_unit_deletion import delete_from_given_learning_unit_year


@login_required
@permission_required('base.can_edit_learningunit_date', raise_exception=True)
def learning_unit_modify_end_date(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    user_person = get_object_or_404(Person, user=request.user)

    if not is_eligible_for_modification_end_date(learning_unit_year, user_person):
        raise PermissionDenied("Learning unit year date is not editable or user has not sufficient rights.")

    form = LearningUnitEndDateForm(request.POST or None, learning_unit=learning_unit_year.learning_unit)
    if form.is_valid():
        academic_year_to_delete = form.cleaned_data['academic_year']

        learning_unit_year_to_delete = learning_unit_year_mdl.search(
            learning_unit=learning_unit_year.learning_unit,
            academic_year_id=academic_year_to_delete
        )

        try:
            learning_unit_year_to_delete = learning_unit_year_to_delete.get()
            return delete_from_given_learning_unit_year(request, learning_unit_year_to_delete.id)

        except LearningUnitYear.DoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 _("There is no existing learning unit year for this academic year"))

    return layout.render(request, 'learning_unit/date_modification.html',
                         {'form': form, 'learning_unit_year': learning_unit_year})
