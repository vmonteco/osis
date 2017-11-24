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

from base.forms.bootstrap import BootstrapForm
from base.forms.offer_year_calendar import OfferYearCalendarForm
from base.models.offer_year_calendar import OfferYearCalendar


class EducationGroupExamenEnrollementsForm(OfferYearCalendarForm):
    class Meta:
        models = OfferYearCalendar
        fields = ['start_date', 'end_date']

class EducationGroupAdministrativeDataForm(BootstrapForm):
    exam_enrollments_2 = forms.DateTimeField()
    exam_enrollments_3 = forms.DateTimeField()

    scores_exam_submission = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'),
                                             input_formats=('%d/%m/%Y', ), required=True)

    dissertation_submission = forms.DateTimeField()
    deliberation = forms.DateTimeField()
    scores_exam_diffusion = forms.DateTimeField()
