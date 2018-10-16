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
from django.utils.functional import cached_property

from base.models.entity_version import EntityVersion
from base.models.enums import organization_type
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class OrganizationAdmin(SerializableModelAdmin):
    list_display = ('title', 'acronym', 'type', 'changed')
    search_fields = ['acronym', 'title']


class Organization(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    type = models.CharField(
        max_length=30,
        blank=True,
        choices=organization_type.ORGANIZATION_TYPE,
    )

    @cached_property
    def latest_version(self):
        return EntityVersion.objects.filter(parent__isnull=True, entity__organization=self)\
            .order_by("start_date").last()

    def __str__(self):
        latest_vers = self.latest_version
        if latest_vers:
            return "{}".format(self.latest_version.title)
        else:
            return ""

    class Meta:
        permissions = (
            ("can_access_organization", "Can access organization"),
        )

    @cached_property
    def title(self):
        return getattr(self.latest_version, "title", "")

    @cached_property
    def logo(self):
        return getattr(self.latest_version, "logo", None)

    @cached_property
    def acronym(self):
        return getattr(self.latest_version, "acronym", "")

    @property
    def country(self):
        # FIXME : Workaround, the address must be directly selectable
        qs = self.organizationaddress_set
        if qs.exists():
            return qs.first().country
        return None


def find_by_id(organization_id):
    return Organization.objects.get(pk=organization_id)
