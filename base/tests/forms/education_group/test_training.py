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
from unittest import mock

from base.forms.education_group.training import TrainingForm
from base.models.enums import education_group_categories
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.forms.education_group.test_common import EducationGroupYearModelFormMixin


class TestTrainingPostponedList(EducationGroupYearModelFormMixin):
    """Unit tests to ensure that TRAINING have a method _postponed_list"""
    def setUp(self):
        self.education_group_type = EducationGroupTypeFactory(
            category=education_group_categories.TRAINING
        )
        super(TestTrainingPostponedList, self).setUp(education_group_type=self.education_group_type)

    @mock.patch('base.business.education_groups.postponement.start', side_effect=None)
    def test_training_have_postponed_list_method(self, mock_postponement_start):
        instance = self.parent_education_group_year
        form = TrainingForm(data={}, instance=instance)
        self.assertTrue(hasattr(form, '_postponed_list'))
        form._postponed_list()
        self.assertTrue(mock_postponement_start.called)
