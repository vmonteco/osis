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
from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Prefetch
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _
from base import models as mdl
from base.forms.bootstrap import BootstrapForm
from base.models.campus import find_administration_campuses
from base.models.entity_version import find_main_entities_version
from base.models.enums import entity_container_year_link_type
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES, INTERNSHIP
from base.models.enums.learning_unit_periodicity import PERIODICITY_TYPES
from base.models.learning_unit_year import check_if_acronym_regex_is_valid
from reference.models.language import find_all_languages
import re
from base.models import entity_container_year as mdl_entity_container_year
from base.models import entity_version as mdl_entity_version

MIN_ACRONYM_LENGTH = 3

MAX_RECORDS = 1000
SERVICE_COURSE = 'SERVICE_COURSE'
PARENT_FACULTY = 'PARENT_FACULTY'


class LearningUnitYearForm(forms.Form):
    academic_year_id = forms.CharField(max_length=10, required=False)
    container_type = subtype = status = forms.CharField(required=False)
    acronym = title = requirement_entity_acronym = allocation_entity_acronym = forms.CharField(
        widget=forms.TextInput(attrs={'size': '10', 'class': 'form-control'}),
        max_length=20, required=False)
    with_entity_subordinated = forms.BooleanField(required=False)

    def clean_acronym(self):
        data_cleaned = self.cleaned_data.get('acronym')
        data_cleaned = _treat_empty_or_str_none_as_none(data_cleaned)
        if data_cleaned and len(data_cleaned) < MIN_ACRONYM_LENGTH:
            raise ValidationError(_('LU_WARNING_INVALID_ACRONYM'))
        elif data_cleaned and len(data_cleaned) >= MIN_ACRONYM_LENGTH and check_if_acronym_regex_is_valid(data_cleaned) is None:
            raise ValidationError(_('LU_ERRORS_INVALID_REGEX_SYNTAX'))
        return data_cleaned

    def clean_academic_year_id(self):
        data_cleaned = self.cleaned_data.get('academic_year_id')
        if data_cleaned == '0':
            return None
        return data_cleaned

    def clean_requirement_entity_acronym(self):
        data_cleaned = self.cleaned_data.get('requirement_entity_acronym')
        if data_cleaned:
            return data_cleaned.upper()
        return data_cleaned

    def clean_allocation_entity_acronym(self):
        data_cleaned = self.cleaned_data.get('allocation_entity_acronym')
        if data_cleaned:
            return data_cleaned.upper()
        return data_cleaned

    def clean(self):
        clean_data = _clean_data(self.cleaned_data)
        return clean_data

    def get_activity_learning_units(self):
        return self.get_learning_units(False)

    def get_learning_units(self, service_course_search):
        clean_data = self.cleaned_data

        entity_container_prefetch = Prefetch('learning_container_year__entitycontaineryear_set',
                                             queryset=mdl.entity_container_year.search(
                                                 link_type=[entity_container_year_link_type.ALLOCATION_ENTITY,
                                                            entity_container_year_link_type.REQUIREMENT_ENTITY])
                                             .prefetch_related(
                                                 Prefetch('entity__entityversion_set', queryset=mdl_entity_version.search(), to_attr='entity_versions')
                                             ),
                                             to_attr='entity_containers_year')

        clean_data['learning_container_year_id'] = _get_filter_learning_container_ids(clean_data)
        learning_units = mdl.learning_unit_year.search(**clean_data) \
            .select_related('academic_year', 'learning_container_year', 'learning_container_year__academic_year') \
            .prefetch_related(entity_container_prefetch) \
            .order_by('academic_year__year', 'acronym')[:MAX_RECORDS + 1]
        list_results = [_append_latest_entities(learning_unit, service_course_search) for learning_unit in learning_units]

        return list_results

    def get_service_course_learning_units(self):
        list_results = self.get_learning_units_service_course(True)
        service_courses = []
        clean_data = self.cleaned_data
        for l in list_results:
            if SERVICE_COURSE in l.entities:
                if l.entities[SERVICE_COURSE] and entity_container_year_link_type.ALLOCATION_ENTITY in l.entities:

                    if clean_data['allocation_entity_acronym'] and not clean_data['requirement_entity_acronym']  :
                        if l.entities[entity_container_year_link_type.ALLOCATION_ENTITY].acronym == clean_data['allocation_entity_acronym']:
                            service_courses.append(l)
                    if clean_data['requirement_entity_acronym'] and not clean_data['allocation_entity_acronym']  :
                        if l.entities[entity_container_year_link_type.REQUIREMENT_ENTITY].acronym == clean_data['requirement_entity_acronym']:
                            service_courses.append(l)
                    if clean_data['requirement_entity_acronym'] and  clean_data['allocation_entity_acronym']  :
                        if l.entities[entity_container_year_link_type.ALLOCATION_ENTITY].acronym == clean_data['allocation_entity_acronym']\
                                and  l.entities[entity_container_year_link_type.REQUIREMENT_ENTITY].acronym == clean_data['requirement_entity_acronym']:
                            service_courses.append(l)

        return service_courses

    def get_learning_units_service_course(self, service_course_search):
        clean_data = self.cleaned_data

        entity_container_prefetch = Prefetch('learning_container_year__entitycontaineryear_set',
                                             queryset=mdl.entity_container_year.search(
                                                 link_type=[entity_container_year_link_type.ALLOCATION_ENTITY,
                                                            entity_container_year_link_type.REQUIREMENT_ENTITY])
                                             .prefetch_related(
                                                 Prefetch('entity__entityversion_set',
                                                          queryset=mdl_entity_version.search(),
                                                          to_attr='entity_versions')
                                             ),
                                             to_attr='entity_containers_year')

        clean_data['learning_container_year_id'] = _get_filter_learning_container_ids(clean_data)
        learning_units = mdl.learning_unit_year.search(**clean_data) \
            .select_related('academic_year', 'learning_container_year', 'learning_container_year__academic_year') \
            .prefetch_related(entity_container_prefetch) \
            .order_by('academic_year__year', 'acronym')
        # same query as get_learning_units but without max records number
        list_results = [_append_latest_entities(learning_unit, service_course_search) for learning_unit in learning_units]

        return list_results


def _clean_data(datas_to_clean):
    return {key: _treat_empty_or_str_none_as_none(value) for (key, value) in datas_to_clean.items()}


def _treat_empty_or_str_none_as_none(data):
    return None if not data or data == "NONE" else data


def _get_filter_learning_container_ids(filter_data):
    requirement_entity_acronym = filter_data.get('requirement_entity_acronym')
    allocation_entity_acronym = filter_data.get('allocation_entity_acronym')
    with_entity_subordinated = filter_data.get('with_entity_subordinated', False)
    entities_id_list = []
    if requirement_entity_acronym:
        entity_ids = _get_entities_ids(requirement_entity_acronym, with_entity_subordinated)
        entities_id_list+= list(mdl.entity_container_year.search(link_type=entity_container_year_link_type.REQUIREMENT_ENTITY,
                                                     entity_id=entity_ids) \
                    .values_list('learning_container_year', flat=True).distinct())
    if allocation_entity_acronym:
        entity_ids = _get_entities_ids(allocation_entity_acronym, False)
        entities_id_list+=list(mdl.entity_container_year.search(link_type=entity_container_year_link_type.ALLOCATION_ENTITY,
                                                                entity_id=entity_ids) \
                               .values_list('learning_container_year', flat=True).distinct())

    return entities_id_list if entities_id_list else None


def _get_entities_ids(requirement_entity_acronym, with_entity_subordinated):
    entities_ids = set()
    entity_versions = mdl.entity_version.search(acronym=requirement_entity_acronym)
    entities_ids |= set(entity_versions.values_list('entity', flat=True).distinct())

    if with_entity_subordinated:
        for entity_version in entity_versions:
            all_descendants = entity_version.find_descendants(entity_version.start_date)
            entities_ids |= {descendant.entity.id for descendant in all_descendants}
    return list(entities_ids)


def is_service_course(learning_unit_yr):
    requirement_entity_version = learning_unit_yr.entities[entity_container_year_link_type.REQUIREMENT_ENTITY]

    entity_container_yr = mdl_entity_container_year.find_requirement_entity(learning_unit_yr.learning_container_year)

    enti = mdl_entity_version.find_parent_faculty_version(requirement_entity_version,
                                                          learning_unit_yr.learning_container_year.academic_year)

    if enti is None and entity_container_yr:
        enti = entity_container_yr.entity
    else:
        enti = enti.entity

    requirement_entity = mdl_entity_version.get_last_version(enti)
    entity_containter_yr_allocation = mdl_entity_container_year.find_allocation_entity(learning_unit_yr.learning_container_year)

    if entity_containter_yr_allocation == requirement_entity_version:
        return False

    if entity_containter_yr_allocation:
        allocation_entity = mdl_entity_version.get_last_version(entity_containter_yr_allocation.entity)
        for entity_descendant in requirement_entity.find_descendants(learning_unit_yr.academic_year.start_date):
            if entity_descendant == allocation_entity:
                return False

    return True


def _append_latest_entities(learning_unit, service_course_search):
    learning_unit.entities = {}
    if learning_unit.learning_container_year and learning_unit.learning_container_year.entity_containers_year:
        for entity_container_yr in learning_unit.learning_container_year.entity_containers_year:
            link_type = entity_container_yr.type
            latest_version = _get_latest_entity_version(entity_container_yr)
            learning_unit.entities[link_type] = latest_version
    if service_course_search:
        if entity_container_year_link_type.REQUIREMENT_ENTITY in learning_unit.entities:

            entity_parent = mdl.entity_version\
                .find_parent_faculty_version(learning_unit.entities[entity_container_year_link_type.REQUIREMENT_ENTITY],
                                             learning_unit.learning_container_year.academic_year)
            if entity_parent:
                learning_unit.entities[PARENT_FACULTY] = entity_parent
            else:
                learning_unit.entities[PARENT_FACULTY] = learning_unit.entities[entity_container_year_link_type.REQUIREMENT_ENTITY]
            if entity_container_year_link_type.REQUIREMENT_ENTITY in learning_unit.entities and \
                entity_container_year_link_type.ALLOCATION_ENTITY in learning_unit.entities and \
                learning_unit.entities[entity_container_year_link_type.REQUIREMENT_ENTITY] != learning_unit.entities[entity_container_year_link_type.ALLOCATION_ENTITY]:
                learning_unit.entities[SERVICE_COURSE] = is_service_course(learning_unit)
            else:
                learning_unit.entities[SERVICE_COURSE] = False
    return learning_unit


def _get_latest_entity_version(entity_container_year):
    entity_version = None
    if entity_container_year.entity.entity_versions:
        entity_version = entity_container_year.entity.entity_versions[-1]
    return entity_version


def create_main_entities_version_list():
    return [(None, "---------"), ] + [(entity_version.id, entity_version.acronym) for entity_version
                                      in find_main_entities_version()]


def create_learning_container_year_type_list():
    return ((None, "---------"),) + LEARNING_CONTAINER_YEAR_TYPES


def create_languages_list():
    return [(language.id, language.name) for language in find_all_languages()]


class CreateLearningUnitYearForm(BootstrapForm):
    acronym = forms.CharField(widget=forms.TextInput(attrs={'maxlength': "15", 'required': True}))
    academic_year = forms.ModelChoiceField(queryset=mdl.academic_year.find_academic_years(), required=True,
                                           empty_label=_('all_label'))
    status = forms.CharField(required=False, widget=forms.CheckboxInput())
    internship_subtype = forms.ChoiceField(choices=((None, "---------"),) +
                                           mdl.enums.internship_subtypes.INTERNSHIP_SUBTYPES,
                                           required=False)
    credits = forms.CharField(widget=forms.TextInput(attrs={'required': True}))
    title = forms.CharField(widget=forms.TextInput(attrs={'required': True}))
    title_english = forms.CharField(required=False, widget=forms.TextInput())
    session = forms.ChoiceField(choices=((None, "---------"),) +
                                mdl.enums.learning_unit_year_session.LEARNING_UNIT_YEAR_SESSION,
                                required=False)
    subtype = forms.CharField(widget=forms.HiddenInput())
    first_letter = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'text-center',
                                                                                 'maxlength': "1",
                                                                                 'readonly': 'readonly'}))
    learning_container_year_type = forms.ChoiceField(choices=lazy(create_learning_container_year_type_list, tuple),
                                                     widget=forms.Select(attrs={'onchange': 'showInternshipSubtype(this.value)'}))
    faculty_remark = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
    other_remark = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
    periodicity = forms.CharField(widget=forms.Select(choices=PERIODICITY_TYPES))
    campus = forms.ModelChoiceField(queryset=find_administration_campuses(),
                                    widget=forms.Select(attrs={'onchange': 'setFirstLetter()'}))
    requirement_entity = forms.ChoiceField(choices=lazy(create_main_entities_version_list, tuple),
                                           widget=forms.Select(attrs={'onchange': 'showAdditionalEntity(this.value, "id_additional_entity_1")'}))
    allocation_entity = forms.ChoiceField(choices=lazy(create_main_entities_version_list, tuple),
                                          required=False)
    additional_entity_1 = forms.ChoiceField(choices=lazy(create_main_entities_version_list, tuple),
                                            required=False,
                                            widget=forms.Select(attrs={'onchange': 'showAdditionalEntity(this.value, "id_additional_entity_2")',
                                                                       'disable': 'disable'}))
    additional_entity_2 = forms.ChoiceField(choices=lazy(create_main_entities_version_list, tuple),
                                            required=False,
                                            widget=forms.Select(attrs={'disable': 'disable'}))
    language = forms.ChoiceField(choices=lazy(create_languages_list, tuple))

    acronym_regex = "^[BLMW][A-Z]{2,4}\d{4}$"

    def clean_acronym(self):
        data_cleaned = self.data.get('first_letter')+self.cleaned_data.get('acronym')
        if data_cleaned:
            return data_cleaned.upper()

    def is_valid(self):
        if not super().is_valid():
            return False
        try:
            academic_year = mdl.academic_year.find_academic_year_by_id(self.data.get('academic_year'))
        except ObjectDoesNotExist:
            return False
        learning_unit_years = mdl.learning_unit_year.find_gte_year_acronym(academic_year, self.data['acronym'])
        learning_unit_years_list = [learning_unit_year.acronym.lower() for learning_unit_year in learning_unit_years]
        if self.data['acronym'] in learning_unit_years_list:
            self.add_error('acronym', _('existing_acronym'))
        elif not re.match(self.acronym_regex, self.cleaned_data['acronym']):
            self.add_error('acronym', _('invalid_acronym'))
        elif self.cleaned_data['learning_container_year_type'] == INTERNSHIP \
                and not (self.cleaned_data['internship_subtype']):
            self._errors['internship_subtype'] = _('field_is_required')
        elif not self.cleaned_data['credits']:
            self._errors['credits'] = _('field_is_required')
            return False
        else:
            return True


