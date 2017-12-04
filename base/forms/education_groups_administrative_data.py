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

from base.forms.bootstrap import BootstrapModelForm
from base.models.offer_year_calendar import OfferYearCalendar
from django.utils.translation import ugettext_lazy as _

DATE_FORMAT = '%d/%m/%Y'
TIME_FORMAT = '%H:%M'
DATETIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT
DATE_RANGE_SPLITTER = ' - '
DATE_RANGE_FORMAT = DATE_FORMAT + DATE_RANGE_SPLITTER + DATE_FORMAT


class DatePickerInput(forms.DateInput):
    def __init__(self, attrs=None, format=DATE_FORMAT):
        if not attrs:
            attrs={'class': 'datepicker form-control',
                   'data-date-format': 'dd/mm/yyyy'}

        super().__init__(attrs)
        self.format = format


class DateTimePickerInput(forms.DateTimeInput):
    def __init__(self, attrs=None, format=DATETIME_FORMAT):
        if not attrs:
            attrs={'class': 'datetimepicker form-control',
                   'data-date-format': 'dd/mm/yyyy hh:ii'}

        super().__init__(attrs)
        self.format = format


class DateRangePickerInput(forms.DateInput):
    def __init__(self, attrs=None, format=DATE_RANGE_FORMAT):
        if not attrs:
            attrs={'class': 'daterange form-control',
                   'data-date-format': 'dd/mm/yyyy - dd/mm/yyyy'}

        super().__init__(attrs)
        self.format = format


class DateRangeField(forms.DateField):

    input_formats = DATE_RANGE_FORMAT
    widget = DateRangePickerInput

    def to_python(self, value):
        values = value.split(DATE_RANGE_SPLITTER)
        start_date = super().to_python(values[0])
        end_date = super().to_python(values[1])
        return start_date, end_date


class CourseEnrollmentForm(BootstrapModelForm):
    range_date = DateRangeField(required=True, label=_("course_enrollment"))

    def clean(self):
        range_date = self.cleaned_data["range_date"]
        if range_date:
            print("be nice with me")
            self.cleaned_data['start_date'] = range_date[0]
            self.cleaned_data['end_date'] = range_date[1]
        super().clean()

    class Meta:
        model = OfferYearCalendar
        fields = []


class AdministrativeDataSession(forms.Form):
    exam_enrollment_range = DateRangeField(required=True, label=_('EXAM_ENROLLMENTS'))

    scores_exam_submission = forms.DateField(widget=DatePickerInput(format=DATE_FORMAT),
                                             input_formats=DATE_FORMAT,
                                             required=True, label=_('marks_presentation'))

    dissertation_submission = forms.DateField(widget=DatePickerInput(format=DATE_FORMAT),
                                              input_formats=DATE_FORMAT,
                                              required=True, label=_('dissertation_presentation'))

    deliberation = forms.DateTimeField(widget=DateTimePickerInput(format=DATETIME_FORMAT),
                                       input_formats=DATETIME_FORMAT,
                                       required=True, label=_('DELIBERATION'))

    scores_exam_diffusion = forms.DateTimeField(widget=DateTimePickerInput(format=DATETIME_FORMAT),
                                                input_formats=DATETIME_FORMAT,
                                                required=True, label=_("scores_diffusion"))

    def clean_exam_enrollment_range(self):
        value = self.cleaned_data.get('exam_enrollment_range')
        if value:
            if value[0] > value[1]:
                raise forms.ValidationError('{} must greater than {}'.format(value[1], value[0]))
            self.cleaned_data['start_date'] = value[0]
            self.cleaned_data['end_date'] = value[1]
        return value
