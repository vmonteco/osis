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
from django.db.models import Q


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
        academic_year = kwargs['academic_year']
        queryset = queryset.filter(Q(parent__academic_year=academic_year)
                                   |Q(child_branch__academic_year=academic_year)
                                   |Q(child_leaf__academic_year=academic_year))

    if 'learning_unit_year' in kwargs:
        queryset = queryset.filter(child_leaf=kwargs['learning_unit_year'])

    return queryset


def find_by_parent(an_education_group_year):
    return GroupElementYear.objects.filter(parent=an_education_group_year)


def find_learning_unit_formations(learn_unit_year):
    root_type_names = education_group_type.search(category=education_group_categories.MINI_TRAINING)\
                                          .exclude(name='Option').values_list('name', flat=True)
    root_categories = [education_group_categories.TRAINING]
    filters = {
        'parent__education_group_type__name': root_type_names,
        'parent__education_group_type__category': root_categories
    }
    return _find_related_root_education_groups(learn_unit_year, filters=filters)


def _find_related_root_education_groups(learn_unit_year, filters=None):
    parents_by_id = _build_parent_list_by_education_group_year_id(learn_unit_year.academic_year, filters=filters)
    return _find_elements(parents_by_id, child_leaf=learn_unit_year.id, filters=filters)


def _build_parent_list_by_education_group_year_id(academic_year, filters=None):
    columns_needed_for_filters = filters.keys() if filters else []
    group_elements = search(academic_year=academic_year) \
        .select_related('education_group_year__education_group_type') \
        .values('parent', 'child_branch', 'child_leaf', *columns_needed_for_filters)
    result = {}
    for group_element_year in group_elements:
        key = _build_child_key(child_branch=group_element_year['child_branch'],
                               child_leaf=group_element_year['child_leaf'])
        result.setdefault(key, []).append(group_element_year)
    return result


def _build_child_key(child_branch=None, child_leaf=None):
    args = [child_leaf, child_branch]
    if not any(args) or all(args):
        raise AttributeError('Only one of the 2 param must bet set (not both of them).')
    if child_leaf:
        branch_part = 'child_leaf'
        id_part = child_leaf
    else:
        branch_part = 'child_branch'
        id_part = child_branch
    return '{branch_part}_{id_part}'.format(**locals())


def _find_elements(group_elements_by_child_id, child_leaf=None, child_branch=None, filters=None):
    roots = []
    group_elements_year = group_elements_by_child_id.get(_build_child_key(child_leaf=child_leaf,
                                                                          child_branch=child_branch))
    if not group_elements_year:
        if child_branch:
            roots.append(child_branch)
    else:
        for group_element_year in group_elements_year:
            parent_id = group_element_year['parent']
            if filters and any(group_element_year[col_name] in values_list for col_name, values_list in filters.items()):
                roots.append(parent_id)
            else:
                roots.extend(_find_elements(group_elements_by_child_id, child_branch=parent_id, filters=filters))
    return roots
