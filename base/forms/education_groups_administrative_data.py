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
from functools import partial

from django import forms

from base.forms.bootstrap import BootstrapModelForm
from base.models.offer_year_calendar import OfferYearCalendar

DATE_FORMAT = '%d/%m/%Y'
TIME_FORMAT = '%H:%M'
DATETIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT

DatePickerInput = partial(forms.DateInput, {'class': 'datepicker',
                                            'data-date-format': 'dd/mm/yyyy'})

DateTimePickerInput = partial(forms.DateTimeInput, {'class': 'datetimepicker',
                                                    'data-date-format': 'dd/mm/yyyy hh:ii'})


class SessionDateForm(BootstrapModelForm):
    start_date = forms.DateField(widget=DatePickerInput(format=DATE_FORMAT),
                                 input_formats=(DATE_FORMAT),
                                 required=True)

    end_date = forms.DateField(widget=DatePickerInput(format=DATE_FORMAT),
                               input_formats=(DATE_FORMAT),
                               required=True)

    class Meta:
        model = OfferYearCalendar
        fields = ['start_date', 'end_date']


class SessionDateTimeForm(SessionDateForm):
    start_date = forms.DateTimeField(widget=DateTimePickerInput(format=DATETIME_FORMAT),
                                     input_formats=DATETIME_FORMAT,
                                     required=True)

    end_date = forms.DateTimeField(widget=DateTimePickerInput(format=DATETIME_FORMAT),
                                   input_formats=DATETIME_FORMAT,
                                   required=True)
