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

from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base.models.learning_unit import LEARNING_UNIT_ACRONYM_REGEX_ALL
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from base.models.learning_unit_year import MINIMUM_CREDITS, MAXIMUM_CREDITS


class ExternalLearningUnitYearAdmin(SerializableModelAdmin):
    list_display = ('external_id', 'acronym', 'credits', 'url', 'learning_unit_year')
    fieldsets = ((None, {'fields': ('acronym', 'credits', 'url', 'learning_unit_year')}),)
    raw_id_fields = ('learning_unit_year', )
    search_fields = ['acronym', 'learning_unit_year__acronym']


class ExternalLearningUnitYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    acronym = models.CharField(max_length=15, db_index=True, verbose_name=_('code'),
                               validators=[RegexValidator(LEARNING_UNIT_ACRONYM_REGEX_ALL)])
    credits = models.DecimalField(max_digits=5, decimal_places=2,
                                  validators=[MinValueValidator(MINIMUM_CREDITS), MaxValueValidator(MAXIMUM_CREDITS)])
    url = models.URLField(max_length=255)
    learning_unit_year = models.OneToOneField('LearningUnitYear')

    class Meta:
        unique_together = ('learning_unit_year', 'acronym',)

    def __str__(self):
        return u"%s" % self.acronym
