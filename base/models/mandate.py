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
from decimal import *

from django.db import models
from django.db.models import When, Case, Q, Sum, Count, IntegerField, F
from django.contrib import admin
from django.utils.translation import ugettext as _

from django.core.validators import MaxValueValidator, MinValueValidator

from base.models import person, session_exam_deadline, \
    academic_year as academic_yr, offer_year, program_manager, tutor
from attribution.models import attribution
from base.models.enums import exam_enrollment_state as enrollment_states, exam_enrollment_justification_type as justification_types, mandate_type as mandate_types
from base.models.exceptions import JustificationValueException
from base.models.utils.admin_extentions import remove_delete_action
from django.db import models
from django.contrib import admin


class MandateAdmin(admin.ModelAdmin):
    list_display = ('education_group', 'function')
    fieldsets = ((None, {'fields': ('education_group',
                                    'function')}),)

    raw_id_fields = ('education_group',)
    search_fields = ['education_group']


class Mandate(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    education_group = models.ForeignKey('EducationGroup', blank=True, null=True)
    function = models.CharField(max_length=20, choices=mandate_types.MANDATE_TYPES)
    qualification = models.CharField(max_length=50,blank=True, null=True )
