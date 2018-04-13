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

from django import forms

from base.forms.bootstrap import BootstrapForm
from base.forms.learning_unit.learning_unit_create import EntitiesVersionChoiceField
from base.forms.utils.choice_field import add_blank
from base.models.academic_year import AcademicYear
from base.models.entity_version import find_main_entities_version
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES_FOR_PROPOSAL_FACULTY
from base.models.person import FACULTY_MANAGER_GROUP

MAX_ACADEMIC_YEAR_FACULTY = datetime.datetime.now().year+4


# # FIXME Merge this with ProposalLearningUnitForm
# class LearningUnitProposalForm(BootstrapForm):
#     entity = EntitiesVersionChoiceField(queryset=find_main_entities_version())
#     folder_id = forms.IntegerField(min_value=0)
#
#
# class LearningUnitProposalCreationForm(forms.Form):
#     def __init__(self, person, *args, **kwargs):
#         super(LearningUnitProposalCreationForm, self).__init__(*args, **kwargs)
#         # When we submit a proposal, we can select all requirement entity available
#         self.fields["requirement_entity"].queryset = find_main_entities_version()
#         if person.user.groups.filter(name=FACULTY_MANAGER_GROUP).exists():
#             self.fields["requirement_entity"].queryset = person.find_main_entities_version
#             self.fields["container_type"].choices = add_blank(LEARNING_CONTAINER_YEAR_TYPES_FOR_PROPOSAL_FACULTY)
#             self.fields["academic_year"].queryset = AcademicYear.objects\
#                 .filter(year__gt=datetime.datetime.now().year)\
#                 .filter(year__lte=MAX_ACADEMIC_YEAR_FACULTY)
