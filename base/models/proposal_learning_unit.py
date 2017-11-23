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
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from base.models.enums import proposal_type, proposal_state


class ProposalLearningUnitAdmin(admin.ModelAdmin):
    list_display = ('learning_unit_year', 'folder', 'type', 'state', )
    fieldsets = ((None, {'fields': ('folder', 'type', 'state', 'initial_data')}),)

    search_fields = ['folder__folder_id', 'folder_entity', 'learning_unit_year__acronym']
    list_filter = ('type', 'state')
    raw_id_fields = ('learning_unit_year', 'folder', )


class ProposalLearningUnit(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    folder = models.ForeignKey('ProposalFolder')
    learning_unit_year = models.ForeignKey('LearningUnitYear')
    type = models.CharField(max_length=50, choices=proposal_type.CHOICES)
    state = models.CharField(max_length=50, choices=proposal_state.CHOICES)
    initial_data = JSONField(default={})


def find_by_learning_unit_year(a_learning_unit_year):
    try:
        return ProposalLearningUnit.objects.get(learning_unit_year=a_learning_unit_year)
    except ObjectDoesNotExist:
        return None
