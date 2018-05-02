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
import datetime
from collections import defaultdict

import itertools
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import OuterRef, Subquery
from django.utils.translation import ugettext_lazy as _

from base import models as mdl
from base.business.entity import get_entities_ids, get_entity_container_list, build_entity_container_prefetch
from base.business.entity_version import SERVICE_COURSE
from base.business.learning_unit_year_with_context import append_latest_entities
from base.forms.common import get_clean_data, treat_empty_or_str_none_as_none, TooManyResultsException
from base.forms.utils.uppercase import convert_to_uppercase
from base.models import learning_unit_year, group_element_year
from base.models.academic_year import AcademicYear, current_academic_year
from base.models.entity import Entity
from base.models.entity_container_year import EntityContainerYear
from base.models.entity_version import EntityVersion
from base.models.enums import entity_container_year_link_type, learning_container_year_types, \
    learning_unit_year_subtypes, active_status, entity_type
from base.models.group_element_year import GroupElementYear
from base.models.learning_unit_year import convert_status_bool

MAX_RECORDS = 1000


class SearchForm(forms.Form):
    MAX_RECORDS = 1000
    ALL_LABEL = (None, _('all_label'))
    ALL_CHOICES = (ALL_LABEL,)

    academic_year_id = forms.ModelChoiceField(
        label=_('academic_year_small'),
        queryset=AcademicYear.objects.all(),
        empty_label=_('all_label'),
    )

    requirement_entity_acronym = forms.CharField(
        max_length=20,
        label=_('requirement_entity_small')
    )

    acronym = forms.CharField(
        max_length=15,
        label=_('code')
    )

    tutor = forms.CharField(
        max_length=20,
        label=_('tutor')
    )

    summary_responsible = forms.CharField(
        max_length=20,
        label=_('summary_responsible')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['academic_year_id'].initial = current_academic_year()
        for field in self.fields.values():
            # In a search form, the fields are never required
            field.required = False

    def clean_requirement_entity_acronym(self):
        return convert_to_uppercase(self.cleaned_data.get('requirement_entity_acronym'))


class LearningUnitYearForm(SearchForm):
    container_type = forms.ChoiceField(
        label=_('type'),
        choices=SearchForm.ALL_CHOICES + learning_container_year_types.LEARNING_CONTAINER_YEAR_TYPES,
    )

    subtype = forms.ChoiceField(
        label=_('subtype'),
        choices=SearchForm.ALL_CHOICES + learning_unit_year_subtypes.LEARNING_UNIT_YEAR_SUBTYPES,
    )

    status = forms.ChoiceField(
        label=_('status'),
        choices=SearchForm.ALL_CHOICES + active_status.ACTIVE_STATUS_LIST[:-1],
    )

    title = forms.CharField(
        max_length=20,
        label=_('title')
    )

    allocation_entity_acronym = forms.CharField(
        max_length=20,
        label=_('allocation_entity_small')
    )

    with_entity_subordinated = forms.BooleanField(label=_('with_entity_subordinated_small'))

    faculty_borrowing = forms.ModelChoiceField(
        label=_("faculty_borrowing"),
        empty_label=_('all_label'),
        queryset=EntityVersion.objects.filter(entity_type=entity_type.FACULTY)
    )

    def __init__(self, *args, **kwargs):
        self.service_course_search = kwargs.pop('service_course_search', False)
        self.borrowed_course_search = kwargs.pop('borrowed_course_search', False)
        super().__init__(*args, **kwargs)

    def clean_acronym(self):
        data_cleaned = self.cleaned_data.get('acronym')
        data_cleaned = treat_empty_or_str_none_as_none(data_cleaned)
        if data_cleaned and learning_unit_year.check_if_acronym_regex_is_valid(data_cleaned) is None:
            raise ValidationError(_('LU_ERRORS_INVALID_REGEX_SYNTAX'))
        return data_cleaned

    def clean_allocation_entity_acronym(self):
        data_cleaned = self.cleaned_data.get('allocation_entity_acronym')
        if data_cleaned:
            return data_cleaned.upper()
        return data_cleaned

    def clean(self):
        return get_clean_data(self.cleaned_data)

    def get_activity_learning_units(self):
        if self.service_course_search:
            return self._get_service_course_learning_units()
        else:
            return self.get_learning_units()

    def get_learning_units(self, service_course_search=None, requirement_entities=None, luy_status=None):
        service_course_search = service_course_search or self.service_course_search
        clean_data = self.cleaned_data
        clean_data['status'] = self._set_status(luy_status)

        if requirement_entities:
            clean_data['requirement_entities'] = requirement_entities

        # TODO Use a queryset instead !!
        clean_data['learning_container_year_id'] = get_filter_learning_container_ids(clean_data)

        # if not service_course_search \
        #         and clean_data \
        #         and mdl.learning_unit_year.count_search_results(**clean_data) > SearchForm.MAX_RECORDS:
        #     raise TooManyResultsException

        learning_units = mdl.learning_unit_year.search(**clean_data) \
            .select_related('academic_year', 'learning_container_year',
                            'learning_container_year__academic_year') \
            .prefetch_related(build_entity_container_prefetch()) \
            .order_by('academic_year__year', 'acronym')

        if self.borrowed_course_search:
            faculty_borrowing_id = clean_data["faculty_borrowing"].entity.id if clean_data.get("faculty_borrowing") \
                else None
            learning_units = filter_is_borrowed_learning_unit_year(learning_units, faculty_borrowing=faculty_borrowing_id)

        # FIXME We must keep a queryset
        return [append_latest_entities(learning_unit, service_course_search) for learning_unit in
                learning_units]

    def _set_status(self, luy_status):
        return convert_status_bool(luy_status) if luy_status else self.cleaned_data['status']

    def _get_service_course_learning_units(self):
        service_courses = []

        for learning_unit in self.get_learning_units(True):
            if not learning_unit.entities.get(SERVICE_COURSE):
                continue

            if self._is_matching_learning_unit(learning_unit):
                service_courses.append(learning_unit)

        return service_courses

    def _is_matching_learning_unit(self, learning_unit):
        allocation_entity_acronym = self.cleaned_data['allocation_entity_acronym']
        requirement_entity_acronym = self.cleaned_data['requirement_entity_acronym']

        allocation_entity_service_course = learning_unit.entities. \
            get(entity_container_year_link_type.ALLOCATION_ENTITY)

        requirement_entity_service_course = learning_unit.entities. \
            get(entity_container_year_link_type.REQUIREMENT_ENTITY)

        return allocation_entity_acronym in (
            allocation_entity_service_course.acronym, None
        ) and requirement_entity_acronym in (
            requirement_entity_service_course.acronym, None
        )


def get_filter_learning_container_ids(filter_data):
    requirement_entity_acronym = filter_data.get('requirement_entity_acronym')
    allocation_entity_acronym = filter_data.get('allocation_entity_acronym')
    with_entity_subordinated = filter_data.get('with_entity_subordinated', False)
    entities_id_list = []

    if requirement_entity_acronym:
        entity_ids = get_entities_ids(requirement_entity_acronym, with_entity_subordinated)
        entities_id_list = get_entity_container_list(entities_id_list,
                                                     entity_ids,
                                                     entity_container_year_link_type.REQUIREMENT_ENTITY)

    if allocation_entity_acronym:
        entity_ids = get_entities_ids(allocation_entity_acronym, False)
        entities_id_list = get_entity_container_list(entities_id_list,
                                                     entity_ids,
                                                     entity_container_year_link_type.ALLOCATION_ENTITY)

    return entities_id_list if entities_id_list else None


def compute_faculty_for_entities(date):
    entities = EntityVersion.objects.current(date).values_list("entity", "parent", "entity_type")
    dict_parent_and_type_of_entity = {entity_id: (parent_id, entity_type) for entity_id, parent_id, entity_type
                                      in entities}
    dict_faculty_of_entity = {}
    for entity_id, tuple_parent_and_type in dict_parent_and_type_of_entity.items():
        faculty = __search_faculty_for_entity(entity_id, tuple_parent_and_type,
                                              dict_parent_and_type_of_entity)
        dict_faculty_of_entity[entity_id] = faculty
    return dict_faculty_of_entity


def __search_faculty_for_entity(entity_id, tuple_parent_and_type, dict_parent_and_type_of_entity):
    parent, type = tuple_parent_and_type
    if type == entity_type.FACULTY:
        return entity_id
    if parent is None or parent not in dict_parent_and_type_of_entity:
        return entity_id
    new_current = parent
    new_value = dict_parent_and_type_of_entity[new_current]
    return __search_faculty_for_entity(new_current, new_value, dict_parent_and_type_of_entity)


def map_learning_unit_year_with_requirement_entity(learning_unit_year_qs):
    entity_container_years = EntityContainerYear.objects.\
        filter(learning_container_year__pk=OuterRef("learning_container_year__pk"),
               type=entity_container_year_link_type.REQUIREMENT_ENTITY)
    learning_unit_years_with_entity = learning_unit_year_qs.values_list("id").\
        annotate(entity=Subquery(entity_container_years.values("entity")))
    return {luy_id: entity_id for luy_id, entity_id in learning_unit_years_with_entity}


def map_learning_unit_year_with_entities_of_education_groups(learning_unit_year_qs):
    formations = group_element_year.find_learning_unit_formations(learning_unit_year_qs, parents_as_instances=False)
    education_group_ids = list(itertools.chain.from_iterable(formations.values()))
    group_element_years = GroupElementYear.objects.filter(child_branch__in=education_group_ids).\
        values_list("child_branch", "child_branch__offeryearentity__entity")

    dict_entity_of_education_group = {education_group_year_id: entity_id for education_group_year_id, entity_id
                                      in group_element_years}

    dict_education_group_year_entities_for_learning_unit_year = {}
    for luy_id, formations_ids in formations.items():
        dict_education_group_year_entities_for_learning_unit_year[luy_id] = \
            [dict_entity_of_education_group.get(formation_id) for formation_id in formations_ids]
    return dict_education_group_year_entities_for_learning_unit_year


def filter_is_borrowed_learning_unit_year(learning_unit_year_qs, faculty_borrowing=None):
    date = datetime.date.today()

    entities_faculty = compute_faculty_for_entities(date)
    map_luy_entity = map_learning_unit_year_with_requirement_entity(learning_unit_year_qs)
    map_luy_education_group_entities = \
        map_learning_unit_year_with_entities_of_education_groups(learning_unit_year_qs)

    for luy in learning_unit_year_qs:
        if __is_borrowed_learning_unit(luy, entities_faculty, map_luy_entity, map_luy_education_group_entities,
                                       faculty_borrowing):
            yield luy


def __is_borrowed_learning_unit(luy, map_entity_faculty, map_luy_entity, map_luy_education_group_entities,
                                faculty_borrowing):
    luy_entity = map_luy_entity.get(luy.id)
    luy_faculty = map_entity_faculty.get(luy_entity)

    if luy_faculty is None:
        return False

    for education_group_entity in map_luy_education_group_entities.get(luy.id, []):
        if luy_faculty != map_entity_faculty.get(education_group_entity) \
                and map_entity_faculty.get(education_group_entity) is not None \
                and (map_entity_faculty.get(education_group_entity) == faculty_borrowing or faculty_borrowing is not None):
            return True
    return False