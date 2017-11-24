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
from django.utils.translation import ugettext_lazy as _

from base.models.person import Person
from base.forms.learning_units import CreateLearningUnitYearForm
from base.models.entity_version import find_main_entities_version
from base.models import entity_container_year, proposal_folder, proposal_learning_unit
from base.models.enums import proposal_type, proposal_state, entity_container_year_link_type, \
    learning_unit_year_subtypes, learning_container_year_types


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
        if not super().is_valid():
            return False
        if self.data["subtype"] != learning_unit_year_subtypes.FULL:
            self.add_error("subtype", _("type_must_be_full"))

        if self.data["internship_subtype"] and \
           self.data["learning_container_year_type"] != learning_container_year_types.INTERNSHIP:
            self.add_error("internship_subtype", _("learning_unit_type_is_not_internship"))

        return len(self.errors.keys()) == 0

    def save(self, learning_unit_year):
        if not self.is_valid():
            raise ValueError("Form is invalid.")

        entities_by_type = \
            entity_container_year.find_entities_grouped_by_linktype(learning_unit_year.learning_container_year)

        initial_data = {
            "learning_container_year": {
                "id": learning_unit_year.learning_container_year.id,
                "acronym": learning_unit_year.acronym,
                "title": learning_unit_year.title,
                "title_english": learning_unit_year.title_english,
                "container_type": learning_unit_year.learning_container_year.container_type,
                "campus": learning_unit_year.learning_container_year.campus.id,
                "language": learning_unit_year.learning_container_year.language.id,
                "in_charge": learning_unit_year.learning_container_year.in_charge
            },
            "learning_unit_year": {
                "id": learning_unit_year.id,
                "acronym": learning_unit_year.acronym,
                "title": learning_unit_year.title,
                "title_english": learning_unit_year.title_english,
                "subtype": learning_unit_year.subtype,
                "internship_subtype": learning_unit_year.internship_subtype,
                "credits": float(learning_unit_year.credits) if learning_unit_year.credits else None,
                "quadrimester": learning_unit_year.quadrimester,
            },
            "learning_unit": {
                "id": learning_unit_year.learning_unit.id,
                "periodicity": learning_unit_year.learning_unit.periodicity
            },
            "entities": {
                entity_container_year_link_type.REQUIREMENT_ENTITY: entities_by_type[entity_container_year_link_type.REQUIREMENT_ENTITY].id if entities_by_type.get(entity_container_year_link_type.REQUIREMENT_ENTITY) else None,
                entity_container_year_link_type.ALLOCATION_ENTITY: entities_by_type[entity_container_year_link_type.ALLOCATION_ENTITY].id if entities_by_type.get(entity_container_year_link_type.ALLOCATION_ENTITY) else None,
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1: entities_by_type[entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1].id if entities_by_type.get(entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1) else None,
                entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2: entities_by_type[entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2].id if entities_by_type.get(entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2) else None
            }
        }

        # Update learning_unit
        learning_unit_year.learning_unit.periodicity = self.cleaned_data['periodicity']
        learning_unit_year.learning_unit.save()

        # Update learning unit year
        learning_unit_year.acronym = self.cleaned_data['acronym']
        learning_unit_year.title = self.cleaned_data['title']
        learning_unit_year.title_english = self.cleaned_data['title_english']
        learning_unit_year.status = self.cleaned_data['status']
        learning_unit_year.quadrimester = self.cleaned_data['quadrimester']
        learning_unit_year.internship_subtype = self.cleaned_data['internship_subtype']
        learning_unit_year.save()

        # Update learning unit container year
        learning_container_year = learning_unit_year.learning_container_year
        learning_container_year.acronym = self.cleaned_data['acronym']
        learning_container_year.title = self.cleaned_data['title']
        learning_container_year.title_english = self.cleaned_data['title_english']
        learning_container_year.language = self.cleaned_data['language']
        learning_container_year.campus = self.cleaned_data['campus']
        learning_container_year.container_type = self.cleaned_data['learning_container_year_type']
        learning_container_year.save()

        # Update requirement entity
        entity_container = entity_container_year.find_by_learning_container_year_and_linktype(learning_container_year,
                                                                                              entity_container_year_link_type.REQUIREMENT_ENTITY)
        if entity_container:
            entity_container.entity = self.cleaned_data["requirement_entity"].entity
            entity_container.save()
        else:
            entity_container_year.EntityContainerYear.objects.create(learning_container_year=learning_container_year,
                                                                     entity=self.cleaned_data["requirement_entity"].entity,
                                                                     type=entity_container_year_link_type.REQUIREMENT_ENTITY)

        if self.cleaned_data["allocation_entity"]:
            entity_container = entity_container_year.find_by_learning_container_year_and_linktype(learning_container_year,
                                                                                                  entity_container_year_link_type.ALLOCATION_ENTITY)
            if entity_container:
                entity_container.entity = self.cleaned_data["allocation_entity"].entity
                entity_container.save()
            else:
                entity_container_year.EntityContainerYear.objects.create(learning_container_year=learning_container_year,
                                                                         entity=self.cleaned_data["allocation_entity"].entity,
                                                                         type=entity_container_year_link_type.ALLOCATION_ENTITY)

        if self.cleaned_data["additional_entity_1"]:
            entity_container = entity_container_year.find_by_learning_container_year_and_linktype(learning_container_year,
                                                                                                  entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1)
            if entity_container:
                entity_container.entity = self.cleaned_data["additional_entity_1"].entity
                entity_container.save()
            else:
                entity_container_year.EntityContainerYear.objects.create(learning_container_year=learning_container_year,
                                                                         entity=self.cleaned_data["additional_entity_1"].entity,
                                                                         type=entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_1)

        if self.cleaned_data["additional_entity_2"]:
            entity_container = entity_container_year.find_by_learning_container_year_and_linktype(learning_container_year,
                                                                                                  entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2)
            if entity_container:
                entity_container.entity = self.cleaned_data["additional_entity_2"].entity
                entity_container.save()
            else:
                entity_container_year.EntityContainerYear.objects.create(learning_container_year=learning_container_year,
                                                                         entity=self.cleaned_data["additional_entity_2"].entity,
                                                                         type=entity_container_year_link_type.ADDITIONAL_REQUIREMENT_ENTITY_2)
        # Create proposal folder
        folder_entity = self.cleaned_data['folder_entity'].entity
        folder_id = self.cleaned_data['folder_id']

        folder = proposal_folder.ProposalFolder.objects.create(entity=folder_entity, folder_id=folder_id)

        # Create proposal learning unit
        proposal_learning_unit.ProposalLearningUnit.objects.create(
            folder=folder,
            learning_unit_year=learning_unit_year,
            type=self.cleaned_data['type_proposal'],
            state=self.cleaned_data['state_proposal'],
            initial_data=initial_data
        )



