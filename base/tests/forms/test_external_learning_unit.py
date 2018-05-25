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

from base.forms.learning_unit.external_learning_unit import ExternalLearningUnitBaseForm, \
    LearningContainerYearExternalModelForm, ExternalLearningUnitModelForm
from base.forms.learning_unit.learning_unit_create import LearningUnitYearModelForm, \
    LearningUnitModelForm
from base.models.enums import learning_unit_year_subtypes, organization_type
from base.models.enums.learning_container_year_types import EXTERNAL
from base.models.enums.learning_unit_year_subtypes import FULL
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.business.entities import create_entities_hierarchy
from base.tests.factories.campus import CampusFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from reference.tests.factories.language import LanguageFactory


def get_valid_external_learning_unit_form_data(academic_year, person, learning_unit_year=None):
    entities = create_entities_hierarchy()
    PersonEntityFactory(person=person, entity=entities['root_entity'], with_child=True)
    buyer = entities['child_one_entity_version']
    organization = OrganizationFactory(type=organization_type.MAIN)
    campus = CampusFactory(organization=organization)

    if not learning_unit_year:
        container_year = LearningContainerYearFactory(academic_year=academic_year, campus=campus)
        learning_unit_year = LearningUnitYearFactory.build(
            acronym='XOSIS1111',
            academic_year=academic_year,
            learning_container_year=container_year,
            subtype=learning_unit_year_subtypes.FULL
        )
    return {
        # Learning unit year data model form
        'acronym_0': learning_unit_year.acronym[0],
        'acronym_1': learning_unit_year.acronym[1:],
        'academic_year': learning_unit_year.academic_year.id,
        'specific_title': learning_unit_year.specific_title,
        'specific_title_english': learning_unit_year.specific_title_english,
        'credits': learning_unit_year.credits,
        'status': learning_unit_year.status,

        # Learning unit data model form
        'faculty_remark': learning_unit_year.learning_unit.faculty_remark,

        # Learning container year data model form
        'campus': learning_unit_year.learning_container_year.campus.id,
        'language': learning_unit_year.learning_container_year.language.id,
        'common_title': learning_unit_year.learning_container_year.common_title,
        'common_title_english': learning_unit_year.learning_container_year.common_title_english,
        'is_vacant': learning_unit_year.learning_container_year.is_vacant,

        # External learning unit model form
        'buyer': buyer.id,
        'external_acronym': 'Gorzyne',
        'external_credits': '5.5',
    }


class TestExternalLearningUnitForm(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.academic_year = create_current_academic_year()
        self.language = LanguageFactory(code='FR')



    def test_external_learning_unit_form_init(self):
        form = ExternalLearningUnitBaseForm(person=self.person, academic_year=self.academic_year)

        context = form.get_context()
        self.assertEqual(context['subtype'], FULL)
        self.assertIsInstance(context['learning_unit_form'], LearningUnitModelForm)
        self.assertIsInstance(context['learning_unit_year_form'], LearningUnitYearModelForm)
        self.assertIsInstance(context['learning_container_year_form'], LearningContainerYearExternalModelForm)
        self.assertIsInstance(context['learning_unit_external_form'], ExternalLearningUnitModelForm)

    def test_external_learning_unit_form_is_valid(self):
        data = get_valid_external_learning_unit_form_data(self.academic_year, self.person)
        form = ExternalLearningUnitBaseForm(person=self.person, academic_year=self.academic_year, data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_external_learning_unit_form_invalid_acronym(self):
        data = get_valid_external_learning_unit_form_data(self.academic_year, self.person)
        data['acronym_0'] = 'L'
        form = ExternalLearningUnitBaseForm(person=self.person, academic_year=self.academic_year, data=data)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual(list(form.errors[0].keys()), ['acronym'])

    def test_external_learning_unit_form_save(self):
        data = get_valid_external_learning_unit_form_data(self.academic_year, self.person)
        form = ExternalLearningUnitBaseForm(person=self.person, academic_year=self.academic_year, data=data)
        self.assertTrue(form.is_valid(), form.errors)
        luy = form.save()

        self.assertIsInstance(luy, LearningUnitYear)
        self.assertEqual(luy.learning_container_year.container_type, EXTERNAL)
        self.assertEqual(luy.acronym[0], 'X')
        self.assertEqual(luy.externallearningunityear.author, self.person)


