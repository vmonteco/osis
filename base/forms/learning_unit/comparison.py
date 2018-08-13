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
from django import forms
from django.utils.translation import ugettext_lazy as _

from base.models.academic_year import AcademicYear

LIMIT_OF_CHOICES = 3


class SelectComparisonYears(forms.Form):

    def __init__(self, *args, **kwargs):
        academic_year = kwargs.pop('academic_year', None)
        self.search_form = kwargs.pop('search_form', None)

        super(SelectComparisonYears, self).__init__(*args, **kwargs)

        if academic_year:
            years = AcademicYear.objects.filter(year__lte=academic_year.year + 1,
                                                year__gte=academic_year.year - 1).order_by('year')
            choices = _get_choices(years)
            self.fields['academic_years'] = forms.ChoiceField(widget=forms.RadioSelect,
                                                              choices=choices,
                                                              required=True,
                                                              label=_('Choose academic years'),
                                                              initial=choices[0])


def _get_choices(academic_years):
    choices = []
    nb_choice = 1
    for academic_yr in academic_years:
        choices.append((academic_yr.year, str(academic_yr) + ' / ' + str(academic_years[nb_choice])))
        nb_choice += 1
        if nb_choice == LIMIT_OF_CHOICES:
            break
    return choices


