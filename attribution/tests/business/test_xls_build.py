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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
import random
from unittest import mock

import factory.fuzzy
from django.contrib import messages
from django.contrib.auth.models import Permission, Group
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.utils.translation import ugettext_lazy as _

import base.business.learning_unit
from base.business import learning_unit as learning_unit_business
from base.forms.learning_unit.learning_unit_create import LearningUnitModelForm
from base.forms.learning_unit.search_form import LearningUnitYearForm, SearchForm
from base.forms.learning_unit_pedagogy import LearningUnitPedagogyForm, SummaryModelForm
from base.forms.learning_unit_specifications import LearningUnitSpecificationsForm, LearningUnitSpecificationsEditForm
from base.models import learning_unit_component
from base.models import learning_unit_component_class
from base.models.academic_year import AcademicYear
from base.models.bibliography import Bibliography
from base.models.enums import entity_container_year_link_type, active_status, education_group_categories
from base.models.enums import internship_subtypes
from base.models.enums import learning_container_year_types, organization_type, entity_type
from base.models.enums import learning_unit_periodicity
from base.models.enums import learning_unit_year_session
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.learning_container_year_types import LEARNING_CONTAINER_YEAR_TYPES_MUST_HAVE_SAME_ENTITIES
from base.models.enums.learning_unit_year_subtypes import FULL
from base.models.person import FACULTY_MANAGER_GROUP
from base.models.person_entity import PersonEntity
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.business.learning_units import GenerateContainer, GenerateAcademicYear
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_achievement import LearningAchievementFactory
from base.tests.factories.learning_class_year import LearningClassYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container import LearningContainerFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_component_class import LearningUnitComponentClassFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.person_entity import PersonEntityFactory
from base.tests.factories.user import SuperUserFactory, UserFactory
from base.views.learning_unit import learning_unit_components, learning_class_year_edit, learning_unit_specifications
from base.views.learning_unit import learning_unit_identification
from base.views.learning_units.search import learning_units
from base.views.learning_units.search import learning_units_service_course
from base.views.learning_units.update import learning_unit_pedagogy
from cms.enums import entity_name
from cms.tests.factories.text_label import TextLabelFactory
from cms.tests.factories.translated_text import TranslatedTextFactory
from osis_common.document import xls_build
from reference.tests.factories.country import CountryFactory
from reference.tests.factories.language import LanguageFactory
from attribution.business import xls_build
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.tests.factories.attribution import AttributionNewFactory

from attribution.models import attribution_charge_new
from attribution.models.enums import function
from attribution.tests.factories.attribution_charge_new import AttributionChargeNewFactory
from attribution.tests.factories.attribution_new import AttributionNewFactory
from base.models.enums import component_type
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from django.utils import timezone
from attribution.business import attribution_charge_new
from base.tests.factories.business.learning_units import GenerateContainer
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.business.learning_unit import LEARNING_UNIT_TITLES

class TestXlsBuild(TestCase):
    def setUp(self):

        generatorContainer = GenerateContainer(datetime.date.today().year-2, datetime.date.today().year)
        self.learning_unit_yr_1 = generatorContainer.generated_container_years[0].learning_unit_year_full
        entity_version_1 = EntityVersionFactory()

        self.learning_unit_yr_1.entities = {
            entity_container_year_link_type.REQUIREMENT_ENTITY: entity_version_1,
            entity_container_year_link_type.ALLOCATION_ENTITY: None
        }

        component_1 = LearningUnitComponentFactory(learning_unit_year=self.learning_unit_yr_1)
        self.attribution_1 = AttributionChargeNewFactory(learning_component_year=component_1.learning_component_year)
        self.attribution_2 = AttributionChargeNewFactory(learning_component_year=component_1.learning_component_year)

        self.attribution_charge_news_1 = [
            self.attribution_1, self.attribution_2
            ]
        self.learning_unit_yr_1.attribution_charge_news = attribution_charge_new.find_attribution_charge_new_by_learning_unit_year(self.learning_unit_yr_1)

    def test_prepare_xls_content_no_data(self):
        self.assertEqual(xls_build.prepare_xls_content([]), [])

    def test_prepare_xls_content_with_data(self):
        attributions = xls_build.prepare_xls_content([self.learning_unit_yr_1])
        self.assertEqual(len(attributions), len(self.attribution_charge_news_1))

    def test_prepare_titles(self):
        self.assertCountEqual(xls_build._prepare_titles(), LEARNING_UNIT_TITLES + xls_build.ATTRIBUTION_TITLES )
