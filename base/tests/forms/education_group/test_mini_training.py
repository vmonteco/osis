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
from unittest import mock

from base.forms.education_group.mini_training import MiniTrainingModelForm, MiniTrainingForm
from base.models.enums import education_group_categories
from base.tests.factories.authorized_relationship import AuthorizedRelationshipFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.forms.education_group.test_common import EducationGroupYearModelFormMixin


class TestMiniTrainingModelForm(EducationGroupYearModelFormMixin):

    def setUp(self):
        self.education_group_type = EducationGroupTypeFactory(
            category=education_group_categories.MINI_TRAINING
        )
        self.form_class = MiniTrainingModelForm
        AuthorizedRelationshipFactory(child_type=self.education_group_type)

        super(TestMiniTrainingModelForm, self).setUp(education_group_type=self.education_group_type)

    def test_fields(self):
        fields = (
            "acronym", "partial_acronym", "education_group_type",
            "title", "title_english", "credits", "active",
            "main_teaching_campus", "academic_year", "remark",
            "remark_english", "min_credits", "max_credits",
            "schedule_type", "management_entity", "keywords"
        )
        self._test_fields(self.form_class, fields)

    def test_init_academic_year_field(self):
        self._test_init_and_disable_academic_year_field(self.form_class)

    def test_init_education_group_type_field(self):
        self._test_init_education_group_type_field(self.form_class, education_group_categories.MINI_TRAINING)

    def test_preselect_entity_version_from_entity_value(self):
        self._test_preselect_entity_version_from_entity_value(self.form_class)


class TestMiniTrainingPostponedList(EducationGroupYearModelFormMixin):
    """Unit tests to ensure that MINI-TRAINING have a method _postponed_list"""

    def setUp(self):
        self.education_group_type = EducationGroupTypeFactory(
            category=education_group_categories.MINI_TRAINING
        )
        super(TestMiniTrainingPostponedList, self).setUp(education_group_type=self.education_group_type)

    @mock.patch('base.business.education_groups.postponement.start', side_effect=None)
    def test_mini_training_have_postponed_list_method(self, mock_postponement_start):
        instance = self.parent_education_group_year
        form = MiniTrainingForm(data={}, instance=instance)
        self.assertTrue(hasattr(form, '_postponed_list'))
        form._postponed_list()
        self.assertTrue(mock_postponement_start.called)

