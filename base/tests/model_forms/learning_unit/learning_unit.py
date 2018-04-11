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
from django.test import TestCase


class TestLearningUnitModelFormInit(TestCase):
    """Tests LearningUnitModelForm.__init__()"""
    def setUp(self):
        pass

    def test_faculty_remark_widget_textarea_rows(self):
        "should assert rows == 5"
        pass

    def test_other_remark_widget_textarea_rows(self):
        "should assert rows == 5"
        pass


class TestLearningUnitModelFormSave(TestCase):
    """Tests LearningUnitModelForm.save()"""
    def setUp(self):
        pass

    def test_case_missing_learning_container_kwarg(self):
        pass

    def test_case_missing_academic_year_kwarg(self):
        pass

    def test_case_creation_periodicity_correctly_saved(self):
        "post_data={'periodicity': BISANNUAL}"
        pass

    def test_case_creation_faculty_remark_correctly_saved(self):
        pass

    def test_case_creation_other_remark_correctly_saved(self):
        pass

    def test_case_update_periodicity_correctly_saved(self):
        "post_data={'periodicity': BISANNUAL}"
        pass

    def test_case_update_faculty_remark_correctly_saved(self):
        pass

    def test_case_update_other_remark_correctly_saved(self):
        pass
