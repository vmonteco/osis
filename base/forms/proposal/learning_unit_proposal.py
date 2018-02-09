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

from django import forms
from django.db.models import Prefetch
from django.utils.translation import ugettext_lazy as _

from base import models as mdl
from base.business.learning_unit_year_with_context import append_latest_entities
from base.models import entity_version as mdl_entity_version
from base.models.academic_year import AcademicYear, current_academic_year
from base.models.enums import entity_container_year_link_type
from base.models.enums import proposal_type, proposal_state
from base.forms import learning_units as learning_units_form
from base.forms.common import get_clean_data, TooManyResultsException

MAX_RECORDS = 1000
ALL_LABEL = (None, _('all_label'))
ALL_CHOICES = (ALL_LABEL,)


def get_entity_folder_id_ordered_by_acronym():
    entities = mdl.proposal_folder.find_entities()
    entities_sorted_by_acronym = sorted(list(entities), key=lambda t: t.most_recent_acronym)

    return [ALL_LABEL] + [(an_entity.pk, an_entity.most_recent_acronym) for an_entity in entities_sorted_by_acronym]


def get_sorted_proposal_type():

    return tuple(sorted(proposal_type.CHOICES, key=lambda item: item[1]))


def get_sorted_proposal_state():
    return tuple(sorted(proposal_state.CHOICES, key=lambda item: item[1]))


class LearningUnitProposalForm(forms.Form):
    academic_year_id = forms.ModelChoiceField(
        label=_('academic_year_small'),
        queryset=AcademicYear.objects.all(),
        empty_label=_('all_label'),
        required=False,
    )

    requirement_entity_acronym = forms.CharField(
        max_length=20,
        required=False,
        label=_('requirement_entity_small')
    )

    entity_folder_id = forms.ChoiceField(
        label=_('folder_entity'),
        choices=get_entity_folder_id_ordered_by_acronym(),
        required=False
    )

    folder_id = forms.IntegerField(min_value=0,
                                   required=False)

    proposal_type = forms.ChoiceField(
        label=_('type'),
        choices=ALL_CHOICES + get_sorted_proposal_type(),
        required=False
    )

    proposal_state = forms.ChoiceField(
        label=_('status'),
        choices=ALL_CHOICES + get_sorted_proposal_state(),
        required=False
    )

    acronym = forms.CharField(
        max_length=15,
        required=False,
        label=_('acronym')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['academic_year_id'].initial = current_academic_year()

    def is_valid(self):
        if not super().is_valid():
            return False

        if not self.has_criteria():
            self.add_error(None, _('minimum_one_criteria'))
            return False
        return True

    def has_criteria(self):
        criteria_present = False
        for name, field in self.fields.items():
            if self.cleaned_data[name]:
                criteria_present = True
                break
        return criteria_present

    def clean_requirement_entity_acronym(self):
        data_cleaned = self.cleaned_data.get('requirement_entity_acronym')
        if data_cleaned:
            return data_cleaned.upper()
        return data_cleaned

    def clean(self):
        if self.cleaned_data and mdl.proposal_learning_unit.count_search_results(**self.cleaned_data) > MAX_RECORDS:
            raise TooManyResultsException
        return get_clean_data(self.cleaned_data)

    def _get_proposal_learning_units(self):
        clean_data = self.cleaned_data
        parent_version_prefetch = Prefetch('parent__entityversion_set',
                                           queryset=mdl_entity_version.search(),
                                           to_attr='entity_versions')

        entity_version_prefetch = Prefetch('entity__entityversion_set',
                                           queryset=mdl_entity_version.search()
                                           .prefetch_related(parent_version_prefetch),
                                           to_attr='entity_versions')
        entity_container_prefetch = Prefetch('learning_unit_year__learning_container_year__entitycontaineryear_set',
                                             queryset=mdl.entity_container_year.search(
                                                 link_type=[entity_container_year_link_type.ALLOCATION_ENTITY,
                                                            entity_container_year_link_type.REQUIREMENT_ENTITY])
                                             .prefetch_related(entity_version_prefetch),
                                             to_attr='entity_containers_year')
        clean_data['learning_container_year_id'] = learning_units_form.get_filter_learning_container_ids(clean_data)
        res = mdl.proposal_learning_unit.search(**clean_data) \
            .select_related('learning_unit_year__academic_year', 'learning_unit_year__learning_container_year',
                            'learning_unit_year__learning_container_year__academic_year') \
            .prefetch_related(entity_container_prefetch) \
            .order_by('learning_unit_year__academic_year__year', 'learning_unit_year__acronym')
        learning_units = \
            [append_latest_entities(learning_unit_proposal.learning_unit_year, None) for learning_unit_proposal in res]
        return {'proposals': res, 'learning_units': learning_units}
