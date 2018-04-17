##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime

from django.utils import timezone

from django.test import TestCase
from django.db import IntegrityError

from base.models.academic_year import AcademicYear
from base.models.learning_achievements import find_by_learning_unit_yr_and_language
from reference.tests.factories.language import LanguageFactory
from base.tests.factories.business.learning_units import GenerateContainer
from base.tests.factories.learning_achievements import LearningAchievementsFactory


now = timezone.now()
A_CODE_NAME = 'AA 1'


class LearningAchievementsTest(TestCase):

    def setUp(self):
        current_academic_year = AcademicYear(year=now.year,
                                             start_date=datetime.date(now.year, now.month, 15),
                                             end_date=datetime.date(now.year + 1, now.month, 28))
        generated_container = GenerateContainer(start_year=current_academic_year.year,
                                                end_year=current_academic_year.year)
        generated_container_first_year = generated_container.generated_container_years[0]
        self.luy = generated_container_first_year.learning_unit_year_full
        self.language_fr = LanguageFactory(code='FR')
        self.language_en = LanguageFactory(code='EN')

    def test_unique(self):

        self.create_lu_achievement(A_CODE_NAME, self.language_fr, self.luy)
        with self.assertRaises(IntegrityError):
            self.create_lu_achievement(A_CODE_NAME, self.language_fr, self.luy)

    def test_find_by_learning_unit_yr_and_language(self):
        luy_achievement = self.create_lu_achievement(A_CODE_NAME, self.language_fr, self.luy)
        self.assertCountEqual(find_by_learning_unit_yr_and_language(self.luy, self.language_en.code), [])
        self.assertCountEqual(find_by_learning_unit_yr_and_language(self.luy, self.language_fr.code), [luy_achievement])

    def create_lu_achievement(self, a_code_name, a_language, a_learning_unit_yr):
        return LearningAchievementsFactory(code_name=a_code_name,
                                           learning_unit_year=a_learning_unit_yr,
                                           language=a_language)
