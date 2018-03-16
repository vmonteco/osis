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
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from base.models.osis_model_admin import OsisModelAdmin
from base.models import entity


class ProposalFolderAdmin(OsisModelAdmin):
    list_display = ('entity', 'folder_id', )

    search_fields = ['folder_id']
    raw_id_fields = ('entity', )


class ProposalFolder(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    entity = models.ForeignKey('Entity')
    folder_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ('entity', 'folder_id', )

    def __str__(self):
        return _("folder_number").format(self.folder_id)


def find_by_entity_and_folder_id(an_entity, a_folder_id):
    try:
        return ProposalFolder.objects.get(entity=an_entity, folder_id=a_folder_id)
    except ObjectDoesNotExist:
        return None


def find_distinct_folder_entities():
    entities = ProposalFolder.objects.distinct('entity').values_list('entity__id', flat=True)
    return entity.Entity.objects.filter(pk__in=entities)
