############################################################################
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
############################################################################
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.models.organization import Organization
from osis_common.models.osis_model_admin import OsisModelAdmin


class OrganizationVersionAdmin(OsisModelAdmin):
    list_display = ('name', 'acronym', 'prefix', 'changed')
    search_fields = ['acronym', 'name']


class OrganizationVersion(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)

    name = models.CharField(
        max_length=255,
        verbose_name=_("name")
    )

    code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("code")
    )

    acronym = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("acronym")
    )

    website = models.URLField(
        max_length=255,
        blank=True,
        verbose_name=_("website")
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name=_("organization")
    )

    start_date = models.DateTimeField(
        verbose_name=_("start date")
    )

    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("end date")
    )

    prefix = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("prefix")
    )

    logo = models.ImageField(
        upload_to='organization_logos',
        null=True,
        blank=True,
        verbose_name=_("logo")
    )

    def __str__(self):
        return "{}".format(self.name)

    def get_absolute_url(self):
        return reverse("organization_read", args=[self.pk])
