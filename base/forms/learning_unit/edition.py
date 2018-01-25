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
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from base.business.learning_unit import LEARNING_UNIT_CREATION_SPAN_YEARS, compute_max_academic_year_adjournment
from base.forms.bootstrap import BootstrapForm
from base.models import academic_year
from base.models.academic_year import AcademicYear
from base.models.enums import learning_unit_periodicity
from base.models.learning_unit import is_old_learning_unit


class LearningUnitEndDateForm(BootstrapForm):
    academic_year = forms.ModelChoiceField(required=False,
                                           queryset=AcademicYear.objects.none(),
                                           empty_label=_('No planned end'))

    def __init__(self, *args, **kwargs):
        self.learning_unit = kwargs.pop('learning_unit')
        super().__init__(*args, **kwargs)
        end_year = self.learning_unit.end_year

        self._set_initial_value(end_year)

        queryset = self._get_academic_years()

        periodicity = self.learning_unit.periodicity
        self.fields['academic_year'].queryset = _filter_biennial(queryset, periodicity)

    def _set_initial_value(self, end_year):
        try:
            self.fields['academic_year'].initial = AcademicYear.objects.get(year=end_year)
        except (AcademicYear.DoesNotExist, AcademicYear.MultipleObjectsReturned):
            self.fields['academic_year'].initial = None


    def _get_academic_years(self):
        current_academic_year = academic_year.current_academic_year()
        max_year = compute_max_academic_year_adjournment()

        if is_old_learning_unit(self.learning_unit):
            raise ValueError(
                'Learning_unit.end_year {} cannot be less than the current academic_year {}'.format(
                    self.learning_unit.end_year, current_academic_year)
            )

        return AcademicYear.objects.filter(year__gte=current_academic_year.year, year__lte=max_year)


def _filter_biennial(queryset, periodicity):
    result = queryset
    if periodicity != learning_unit_periodicity.ANNUAL:
        is_odd = periodicity == learning_unit_periodicity.BIENNIAL_ODD
        result = queryset.annotate(odd=F('year') % 2).filter(odd=is_odd)
    return result
