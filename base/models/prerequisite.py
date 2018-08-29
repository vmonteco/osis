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
#############################################################################
from django.core import validators
from django.db import models

from osis_common.models.osis_model_admin import OsisModelAdmin

ACRONYM_REGEX = r'[BLMWX][A-Z]{2,4}\d{4}'
NO_PREREQUISITE_REGEX = r''
UNIQUE_PREREQUISITE_REGEX = r'{acronym_regex}'.format(acronym_regex=ACRONYM_REGEX)
ELEMENT_REGEX = r'({acronym_regex}|\({acronym_regex} (?(AND_OPERATOR)OU|ET) {acronym_regex}( (?(AND_OPERATOR)OU|ET) {acronym_regex})*\))'.format(acronym_regex=ACRONYM_REGEX)
MULTIPLE_PREREQUISITES_REGEX = '{acronym_regex} ((?P<AND_OPERATOR>ET)|OU) {element_regex}( (?(AND_OPERATOR)ET|OU) {element_regex})*'.format(acronym_regex=ACRONYM_REGEX, element_regex=ELEMENT_REGEX)
PREREQUISITE_SYNTAX_REGEX = r'^({no_element_regex}|{unique_element_regex}|{multiple_elements_regex})$'.format(
    no_element_regex=NO_PREREQUISITE_REGEX,
    unique_element_regex=UNIQUE_PREREQUISITE_REGEX,
    multiple_elements_regex=MULTIPLE_PREREQUISITES_REGEX)
prerequisite_syntax_validator = validators.RegexValidator(regex=PREREQUISITE_SYNTAX_REGEX)


class PrerequisiteAdmin(OsisModelAdmin):
    list_display = ('learning_unit_year', 'education_group_year', 'prerequisite')
    raw_id_fields = ('learning_unit_year', 'education_group_year')
    list_filter = ('education_group_year__academic_year',)
    search_fields = ['learning_unit_year__acronym', 'education_group_year__acronym',
                     'education_group_year__partial_acronym']


class Prerequisite(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    learning_unit_year = models.ForeignKey("LearningUnitYear")
    education_group_year = models.ForeignKey("EducationGroupYear")
    prerequisite = models.CharField(blank=True, max_length=240, default="", validators=[prerequisite_syntax_validator])

    class Meta:
        unique_together = ('learning_unit_year', 'education_group_year')

    def __str__(self):
        return "{}{} : {}".format(self.education_group_year, self.learning_unit_year, self.prerequisite)
