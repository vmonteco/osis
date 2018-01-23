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
from django import forms
from django.utils.translation import ugettext_lazy as _

from base.forms.bootstrap import BootstrapForm
from base.models.academic_year import AcademicYear
from base.views.learning_unit import LEARNING_UNIT_CREATION_SPAN_YEARS


class LearningUnitEndDateForm(BootstrapForm):

    academic_year = forms.ModelChoiceField(required=False,
                                           queryset=AcademicYear.objects.none(),
                                           empty_label=_('Whiteout validity end date'))

    def __init__(self, *args, **kwargs):
        learning_unit = kwargs.pop('learning_unit')
        super().__init__(*args, **kwargs)
        end_year = learning_unit.end_year

        self.fields['academic_year'].queryset = AcademicYear.objects.filter(
            year__gte=learning_unit.start_year, year__lte=(end_year + LEARNING_UNIT_CREATION_SPAN_YEARS)
        )
        try:
            self.fields['academic_year'].initial = AcademicYear.objects.get(year=end_year)
        except (AcademicYear.DoesNotExist, AcademicYear.MultipleObjectsReturned):
            self.fields['academic_year'].initial = None


