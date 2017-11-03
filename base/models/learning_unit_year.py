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
import re
from django.db import models

from base.models.enums.learning_unit_year_subtypes import FULL, PARTIM
from base.models.group_element_year import GroupElementYear
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin

from base.models import entity_container_year, learning_unit_enrollment, learning_unit_component
from base.models.enums import learning_unit_year_subtypes, learning_container_year_types, internship_subtypes, \
    learning_unit_year_session, entity_container_year_link_type, learning_unit_year_quadrimesters
from django.utils.translation import ugettext_lazy as _


AUTHORIZED_REGEX_CHARS = "$*+.^"
REGEX_ACRONYM_CHARSET = "[A-Z0-9" + AUTHORIZED_REGEX_CHARS + "]+"


class LearningUnitYearAdmin(SerializableModelAdmin):
    list_display = ('external_id', 'acronym', 'title', 'academic_year', 'credits', 'changed', 'structure', 'status')
    fieldsets = ((None, {'fields': ('academic_year', 'learning_unit', 'acronym', 'title', 'title_english', 'credits',
                                    'decimal_scores', 'structure', 'learning_container_year',
                                    'subtype', 'status', 'internship_subtype', 'session', 'quadrimester')}),)
    list_filter = ('academic_year', 'decimal_scores')
    raw_id_fields = ('learning_unit', 'learning_container_year', 'structure')
    search_fields = ['acronym', 'structure__acronym', 'external_id']


class LearningUnitYear(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    academic_year = models.ForeignKey('AcademicYear')
    learning_unit = models.ForeignKey('LearningUnit')
    learning_container_year = models.ForeignKey('LearningContainerYear', blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    acronym = models.CharField(max_length=15, db_index=True)
    title = models.CharField(max_length=255)
    title_english = models.CharField(max_length=250, blank=True, null=True)
    subtype = models.CharField(max_length=50, blank=True, null=True,
                               choices=learning_unit_year_subtypes.LEARNING_UNIT_YEAR_SUBTYPES)
    credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    decimal_scores = models.BooleanField(default=False)
    structure = models.ForeignKey('Structure', blank=True, null=True)
    internship_subtype = models.CharField(max_length=50, blank=True, null=True,
                                          choices=internship_subtypes.INTERNSHIP_SUBTYPES)
    status = models.BooleanField(default=False)
    session = models.CharField(max_length=50, blank=True, null=True,
                               choices=learning_unit_year_session.LEARNING_UNIT_YEAR_SESSION)
    quadrimester = models.CharField(max_length=4, blank=True, null=True,
                                    choices=learning_unit_year_quadrimesters.LEARNING_UNIT_YEAR_QUADRIMESTERS)

    def __str__(self):
        return u"%s - %s" % (self.academic_year, self.acronym)

    @property
    def subdivision(self):
        if self.acronym and self.learning_container_year:
            return self.acronym.replace(self.learning_container_year.acronym, "")
        return None

    @property
    def parent(self):
        if self.subdivision:
            return LearningUnitYear.objects.filter(
                subtype=learning_unit_year_subtypes.FULL,
                learning_container_year=self.learning_container_year,
                learning_container_year__acronym=self.learning_container_year.acronym,
                learning_container_year__container_type=learning_container_year_types.COURSE
            ).first()
        return None

    @property
    def same_container_learning_unit_years(self):
        return LearningUnitYear.objects.filter(
            learning_container_year=self.learning_container_year
        ).order_by('acronym')

    @property
    def allocation_entity(self):
        entity_container_yr = entity_container_year.search(
            link_type=entity_container_year_link_type.ALLOCATION_ENTITY,
            learning_container_year=self.learning_container_year
        ).first()
        return entity_container_yr.entity if entity_container_yr else None

    def delete(self, msg=[], *args, **kwargs):
        next_year = self.get_learning_unit_next_year()
        if next_year:
            next_year.delete(msg)

        if self.learning_container_year and self.subtype == FULL:
            self.learning_container_year.delete(msg)

        for component in self.get_learning_unit_components():
            component.delete(msg)

        result = super().delete(*args, **kwargs)

        subtype = _('The partim') if self.subtype == PARTIM else _('The learning unit')
        msg.append(_('%(subtype)s %(acronym)s has been deleted for the year %(year)s') \
                   % {'subtype': subtype,
                      'acronym':  self.acronym,
                      'year': self.academic_year})
        return result

    def is_deletable(self, msg):
        enrollment_count = len(learning_unit_enrollment.find_by_learning_unit_year(self))
        if enrollment_count > 0:
            subtype = _('the partim') if self.subtype == PARTIM else _('the learning unit')
            msg.append(_("There is %(count)d enrollments in %(subtype)s %(acronym)s for the year %(year)s") %
                       {'subtype': subtype,
                        'acronym': self.acronym,
                        'year': self.academic_year,
                        'count': enrollment_count})

        if self.subtype == FULL and self.learning_container_year:
            self.learning_container_year.is_deletable(msg)

        for component in self.get_learning_unit_components():
            component.is_deletable(msg)

        for group_element_year in self.get_group_elements_year():
            group_element_year.is_deletable(msg)

        next_year = self.get_learning_unit_next_year()
        if next_year:
            next_year.is_deletable(msg)

        return not msg

    def get_partims_related(self):
        if self.subtype == FULL and self.learning_container_year:
            return self.learning_container_year.get_partims_related()

    def get_learning_unit_components(self):
        return learning_unit_component.find_by_learning_unit_year(self)

    def get_group_elements_year(self):
        return GroupElementYear.objects.filter(child_leaf=self).select_related('parent')

    def get_learning_unit_next_year(self):
        try:
            return LearningUnitYear.objects.get(learning_unit=self.learning_unit,
                                                academic_year__year=(self.academic_year.year+1))
        except LearningUnitYear.DoesNotExist:
            return None

    @property
    def in_charge(self):
        return self.learning_container_year and self.learning_container_year.in_charge


def find_by_id(learning_unit_year_id):
    return LearningUnitYear.objects.select_related('learning_container_year__learning_container') \
        .get(pk=learning_unit_year_id)


def find_by_acronym(acronym):
    return LearningUnitYear.objects.filter(acronym=acronym) \
        .select_related('learning_container_year')


def _is_regex(acronym):
    return set(AUTHORIZED_REGEX_CHARS).intersection(set(acronym))


def search(academic_year_id=None, acronym=None, learning_container_year_id=None, learning_unit=None,
           title=None, subtype=None, status=None, container_type=None, *args, **kwargs):
    queryset = LearningUnitYear.objects

    if academic_year_id:
        queryset = queryset.filter(academic_year=academic_year_id)

    if acronym:
        if _is_regex(acronym):
            queryset = queryset.filter(acronym__iregex=r"(" + acronym + ")")
        else:
            queryset = queryset.filter(acronym__icontains=acronym)

    if learning_container_year_id is not None:
        if isinstance(learning_container_year_id, list):
            queryset = queryset.filter(learning_container_year__in=learning_container_year_id)
        elif learning_container_year_id:
            queryset = queryset.filter(learning_container_year=learning_container_year_id)

    if learning_unit:
        queryset = queryset.filter(learning_unit=learning_unit)

    if title:
        queryset = queryset.filter(title__icontains=title)

    if subtype:
        queryset = queryset.filter(subtype=subtype)

    if status:
        queryset = queryset.filter(status=status)

    if container_type:
        queryset = queryset.filter(learning_container_year__container_type=container_type)

    return queryset.select_related('learning_container_year')


def find_gte_year_acronym(academic_yr, acronym):
    return LearningUnitYear.objects.filter(academic_year__year__gte=academic_yr.year,
                                           acronym__iexact=acronym)


def find_lt_year_acronym(academic_yr, acronym):
    return LearningUnitYear.objects.filter(academic_year__year__lt=academic_yr.year,
                                           acronym__iexact=acronym).order_by('academic_year')


def check_if_acronym_regex_is_valid(acronym):
    if isinstance(acronym, str):
        return re.fullmatch(REGEX_ACRONYM_CHARSET, acronym.upper())
