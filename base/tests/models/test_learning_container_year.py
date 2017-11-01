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
import datetime

from django.test import TestCase

from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from base.models import learning_container_year
from base.models.enums import learning_unit_year_subtypes
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class LearningContainerYearTest(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=timezone.now().year)

    def test_find_by_id_with_id(self):
        l_container_year = LearningContainerYearFactory()
        self.assertEqual(l_container_year, learning_container_year.find_by_id(l_container_year.id))

    def test_find_by_id_with_wrong_value(self):
        with self.assertRaises(ValueError):
            learning_container_year.find_by_id("BAD VALUE")

    def test_is_deletable(self):
        l_container_year = LearningContainerYearFactory()
        l_unit_1 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.FULL)
        msg = []
        self.assertTrue(l_container_year.is_deletable(msg))
        self.assertListEqual(msg, [])

        l_unit_2 = LearningUnitYearFactory(acronym="LBIR1212", learning_container_year=l_container_year,
                                           academic_year=self.academic_year, subtype=learning_unit_year_subtypes.PARTIM)

        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)
        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)
        LearningUnitEnrollmentFactory(learning_unit_year=l_unit_2)

        group_1 = GroupElementYearFactory(child_leaf=l_unit_2)
        group_2 = GroupElementYearFactory(child_leaf=l_unit_2)

        component = LearningUnitComponentFactory(learning_unit_year=l_unit_2)
        attribution_charge_1 = AttributionChargeNewFactory(learning_component_year=component.learning_component_year)
        attribution_charge_2 = AttributionChargeNewFactory(learning_component_year=component.learning_component_year)

        l_container_year.is_deletable(msg)
        self.assertEqual(_("There is %(count)d enrollments in %(subtype)s %(acronym)s for the year %(year)s")
                      % {'subtype': _('the partim'),
                         'acronym': l_unit_2.acronym,
                         'year': l_unit_2.academic_year,
                         'count': 3},
                      msg[0])

        msg_delete_tutor = _("%(subtype)s %(acronym)s is assigned to %(tutor)s for the year %(year)s")
        self.assertIn(msg_delete_tutor % {'subtype': _('The partim'),
                                          'acronym': l_unit_2.acronym,
                                          'year': l_unit_2.academic_year,
                                          'tutor': attribution_charge_1.attribution.tutor},
                      msg)
        self.assertIn(msg_delete_tutor % {'subtype': _('The partim'),
                                          'acronym': l_unit_2.acronym,
                                          'year': l_unit_2.academic_year,
                                          'tutor': attribution_charge_2.attribution.tutor},
                      msg)

        msg_delete_offer_type = _(
            '%(subtype)s %(acronym)s is included in the group %(group)s of the program %(program)s for the year %(year)s')

        self.assertIn(msg_delete_offer_type
                      % {'subtype': _('The partim'),
                         'acronym': l_unit_2.acronym,
                         'group': group_1.parent.acronym,
                         'program': group_1.parent.education_group_type,
                         'year': l_unit_2.academic_year},
                      msg)
        self.assertIn(msg_delete_offer_type
                      % {'subtype': _('The partim'),
                         'acronym': l_unit_2.acronym,
                         'group': group_2.parent.acronym,
                         'program': group_2.parent.education_group_type,
                         'year': l_unit_2.academic_year},
                      msg)
