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
from django.contrib import admin
from base.models.enums import sessions_derogation
from base.models.enums import education_group_categories
from base.models import education_group_type


class GroupElementYearAdmin(admin.ModelAdmin):
    list_display = ('parent', 'child_branch', 'child_leaf',)
    fieldsets = ((None, {'fields': ('parent', 'child_branch', 'child_leaf', 'absolute_credits','relative_credits',
                                    'min_credits', 'max_credits', 'is_mandatory', 'block', 'current_order',
                                    'own_comment', 'sessions_derogation','minor_access', 'comment',
                                    'comment_english',)}),)
    raw_id_fields = ('parent', 'child_branch', 'child_leaf',)


class GroupElementYear(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed = models.DateTimeField(null=True, auto_now=True)
    parent = models.ForeignKey('EducationGroupYear', related_name='parent', blank=True, null=True)
    child_branch = models.ForeignKey('EducationGroupYear', related_name='child_branch', blank=True, null=True)
    child_leaf = models.ForeignKey('LearningUnitYear', related_name='child_leaf', blank=True, null=True)
    absolute_credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    relative_credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    min_credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    max_credits = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_mandatory = models.BooleanField(default=False)
    block = models.CharField(max_length=7, blank=True, null=True)
    current_order = models.IntegerField(blank=True, null=True)
    minor_access = models.BooleanField(default=False)
    comment = models.CharField(max_length=500, blank=True, null=True)
    comment_english = models.CharField(max_length=500, blank=True, null=True)
    own_comment = models.CharField(max_length=500, blank=True, null=True)
    sessions_derogation = models.CharField(max_length=65,
                                           choices=sessions_derogation.SessionsDerogationTypes.choices(),
                                           default=sessions_derogation.SessionsDerogationTypes.SESSION_UNDEFINED.value)


def search(**kwargs):
    queryset = GroupElementYear.objects

    if 'academic_year' in kwargs:
        queryset = queryset.filter(child_branch__academic_year=kwargs['academic_year'])

    if 'learning_unit_year' in kwargs:
        queryset = queryset.filter(child_leaf=kwargs['learning_unit_year'])

    return queryset


def find_by_parent(an_education_group_year):
    return GroupElementYear.objects.filter(parent=an_education_group_year)


def find_related_root_education_groups(learn_unit_year):
    default_root_type_names = education_group_type.search(category=education_group_categories.MINI_TRAINING)\
                                                  .exclude(name='Option').values_list('name')
    default_root_categories = [education_group_categories.TRAINING]
    filters = {
        'parent__education_group_type__name': default_root_type_names,
        'parent__education_group_type__category': default_root_categories
    }
    _find_related_root_education_groups(learn_unit_year, filters=filters)


def _find_related_root_education_groups(learn_unit_year, filters=None):
    parents_by_id = _build_parent_list_by_education_group_year_id(learn_unit_year)
    direct_parent_ids = search(learning_unit_year=learn_unit_year).values_list('parent')
    return _find_elements(direct_parent_ids, parents_by_id, filters)


def _build_parent_list_by_education_group_year_id(learn_unit_year, filters=None):
    columns_needed_for_filters = filters.keys() if filters else []
    group_elements = search(academic_year=learn_unit_year.academic_year) \
        .select_related('education_group_year__education_group_type') \
        .values('parent', 'child_branch', *columns_needed_for_filters)
    result = {}
    for group_element_year in group_elements:
        result.setdefault(group_element_year['child_branch'], []).append(group_element_year)
        result.setdefault(group_element_year['parent'], [])
    return result


def _find_elements(direct_parent_ids, parents_by_id, filters=None):
    roots = []
    for child in direct_parent_ids:
        child_id = child['child_branch']
        # parent_id = child_branch['parent']
        if filters and any(child[col_name] in values_list for col_name, values_list in filters.items()):
            roots.append(child)
        elif not parents_by_id[child_id]:
            roots.append(child)
        else:
            roots.extend(_find_elements(parents_by_id[child], parents_by_id, filters=filters))
    return roots
