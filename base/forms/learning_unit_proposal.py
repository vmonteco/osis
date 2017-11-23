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

from base.models.person import Person
from base.forms.learning_units import CreateLearningUnitYearForm
from base.models.entity_version import find_main_entities_version
from base.models import entity_container_year
from base.models.enums import proposal_type, proposal_state, entity_container_year_link_type


def add_none_choice(choices):
    return ((None, "-----"),) + choices


class LearningUnitProposalModificationForm(CreateLearningUnitYearForm):
    type_proposal = forms.ChoiceField(choices=add_none_choice(proposal_type.CHOICES))
    state_proposal = forms.ChoiceField(choices=add_none_choice(proposal_state.CHOICES))
    person = forms.ModelChoiceField(queryset=Person.objects.all(), widget=forms.HiddenInput())
    folder_entity = forms.ModelChoiceField(queryset=find_main_entities_version())
    folder_id = forms.IntegerField(min_value=0)
    date = forms.DateField()

    def is_valid(self):
        # TODO ne peut être que full subtype
        # TODO ne peut pas switch de learning_container_type
        return super().is_valid()

    def save(self, learning_unit_year):
        if not self.is_valid():
            raise ValueError

        # Update learning unit year
        learning_unit_year.acronym = self.cleaned_data['acronym']
        learning_unit_year.title = self.cleaned_data['title']
        learning_unit_year.title_english = self.cleaned_data['title_english']
        learning_unit_year.status = self.cleaned_data['status']
        learning_unit_year.quadrimester = self.cleaned_data['quadrimester']
        learning_unit_year.save()

        # Update learning unit container year
        learning_container_year = learning_unit_year.learning_container_year
        learning_container_year.acronym = self.cleaned_data['acronym']
        learning_container_year.title = self.cleaned_data['title']
        learning_container_year.title_english = self.cleaned_data['title_english']
        learning_container_year.language = self.cleaned_data['language']
        learning_container_year.campus = self.cleaned_data['campus']

        # Update requirement entity
        entity_version = self.cleaned_data['requirement_entity']
        entity = entity_version.entity
        requirement_entity_container_year = entity_container_year.search(
            learning_container_year=learning_container_year,
            link_type=entity_container_year_link_type.REQUIREMENT_ENTITY
        )
        requirement_entity_container_year.update(entity=entity)


