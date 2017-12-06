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
from django.utils import formats

from base.forms.bootstrap import BootstrapModelForm
from base.models import offer_year_calendar, session_exam_calendar
from base.models.enums import academic_calendar_type
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


class DateRangePickerInput(forms.TextInput):
    def __init__(self, attrs=None, format=DATE_RANGE_FORMAT):
        if not attrs:
            attrs={'class': 'daterange form-control',
                   'data-date-format': 'dd/mm/yyyy - dd/mm/yyyy'}

        super().__init__(attrs)
        self.format = format

    def format_value(self, value):
        if isinstance(value, tuple):
            return self.__format_date(value[0]) + DATE_RANGE_SPLITTER + self.__format_date(value[1])
        else:
            return value

    def __format_date(self, value):
        return formats.localize_input(value, DATE_FORMAT)


class DateRangeField(forms.Field):
    input_formats = DATE_RANGE_FORMAT
    widget = DateRangePickerInput

    def __init__(self, base=forms.DateField(), input_formats=None, **kwargs):
        """
        :param base: can be either DateField or DateTimeField, which will be used to do conversions for beginning and end of interval.
        :param input_formats: is passed into base if present
        """
        super(DateRangeField, self).__init__(**kwargs)
        self.base = base
        if input_formats is not None:
            self.base.input_formats = input_formats

    def to_python(self, value):
        values = value.split(DATE_RANGE_SPLITTER)
        start_date = self.base.to_python(values[0])
        end_date = self.base.to_python(values[1])
        return start_date, end_date


class CourseEnrollmentForm(BootstrapModelForm):
    range_date = DateRangeField(required=True, label=_("course_enrollment"))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance=kwargs.get('instance')
        if instance:
            self.fields['range_date'].initial = (instance.start_date, instance.end_date)

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

    def __init__(self, *args, **kwargs):
        self.education_group_year = kwargs.pop('education_group_year')
        self.session = kwargs.pop('session')
        self.list_offer_year_calendar = kwargs.pop('list_offer_year_calendar')
        super().__init__(*args, **kwargs)

        if self.list_offer_year_calendar:
            self._init_fields()

    def _init_fields(self):
        for name, field in self.fields.items():
            if name == 'exam_enrollment_range':
                ac_type = academic_calendar_type.EXAM_ENROLLMENTS
            elif name == 'scores_exam_submission':
                ac_type = academic_calendar_type.SCORES_EXAM_SUBMISSION
            elif name == 'dissertation_submission':
                ac_type = academic_calendar_type.DISSERTATION_SUBMISSION
            elif name == 'deliberation':
                ac_type = academic_calendar_type.DELIBERATION
            elif name == 'scores_exam_diffusion':
                ac_type = academic_calendar_type.SCORES_EXAM_DIFFUSION
            else:
                ac_type = None

            self._init_field(field, ac_type)

    def _init_field(self, field, ac_type):
        oyc = self.list_offer_year_calendar.filter(academic_calendar__reference=ac_type).first()
        if oyc:
            if isinstance(field, DateRangeField):
                field.initial = (oyc.start_date, oyc.end_date)
            else:
                field.initial = oyc.start_date

    def save(self):
        print(self.cleaned_data)





class AdministrativeData(forms.BaseFormSet):

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['session'] = index + 1

        education_group_year = kwargs.get('education_group_year')
        if not education_group_year:
            return kwargs

        q = offer_year_calendar.find_by_education_group_year(education_group_year)
        sessions = session_exam_calendar.find_by_session_and_academic_year(index+1, education_group_year.academic_year)
        academic_calendar_list = [s.academic_calendar for s in sessions]
        kwargs['list_offer_year_calendar'] = q.filter(academic_calendar__in=academic_calendar_list)\
            if academic_calendar_list else None

        return kwargs

    def save(self):
        for form in self.forms:
            form.save()
