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
from django import template

register = template.Library()


@register.inclusion_tag('templatetags/admission_condition_table_row.html')
def render_condition_rows(section_name, header_text, records, condition):
    return {
        'section_name': section_name,
        'header_text': header_text,
        'records': records,
        'condition': condition,
    }


@register.inclusion_tag('templatetags/admission_condition_text.html')
def render_condition_text(section_name, text, field, condition):
    return {
        'section': section_name,
        'text': text,
        'field': field,
        'condition': condition,
    }
