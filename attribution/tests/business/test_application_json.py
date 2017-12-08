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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from datetime import date
from django.test import TestCase
from attribution.business import application_json
from attribution.tests.factories.tutor_application import TutorApplicationFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class AttributionJsonTest(TestCase):
    def setUp(self):
        today = date.today()
        self.academic_year = AcademicYearFactory(year=today.year, start_date=today)
        self.l_container = LearningContainerYearFactory(academic_year=self.academic_year, acronym="LBIR1210",
                                                        in_charge=True)
        self.tutor_1 = TutorFactory(person=PersonFactory(first_name="Tom", last_name="Dupont", global_id='00012345'))
        self.tutor_application = TutorApplicationFactory(tutor=self.tutor_1, learning_container_year=self.l_container)

    def test_build_attributions_json(self):
        application_list = application_json._compute_list()
        self.assertIsInstance(application_list, list)
        self.assertEqual(len(application_list), 1)


