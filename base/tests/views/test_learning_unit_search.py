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
from unittest import mock
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
# from base.forms import learning_unit_search
from base.forms import learning_unit_search
from base.forms.learning_unit_creation import CreateLearningUnitYearForm
from base.models import learning_unit_component
from base.models import learning_unit_component_class
from base.models.academic_year import AcademicYear
from base.models.enums import learning_container_year_types, organization_type, entity_type
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.internship_subtypes import TEACHING_INTERNSHIP
from base.models.enums.learning_container_year_types import COURSE
from base.models.enums.learning_unit_periodicity import ANNUAL
from base.models.enums.learning_unit_year_subtypes import FULL
from base.models.enums.learning_unit_year_session import SESSION_P23
from base.models.learning_unit import LearningUnit
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory, build_future_academic_years
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_unit_component_class import LearningUnitComponentClassFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_class_year import LearningClassYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container import LearningContainerFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.models.enums import entity_container_year_link_type
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import SuperUserFactory
from base.business import learning_unit as learning_unit_business
from django.utils.translation import ugettext_lazy as _
from reference.tests.factories.country import CountryFactory
from reference.tests.factories.language import LanguageFactory


OK = 200
ACCESS_DENIED = 401


class LearningUnitSearchTest(TestCase):
    def setUp(self):
        today = datetime.date.today()
        # self.academic_year_1 = AcademicYearFactory.build(start_date=today.replace(year=today.year+1),
        #                                                  end_date=today.replace(year=today.year+2),
        #                                                  year=today.year+1)
        # self.academic_year_2 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 2),
        #                                                  end_date=today.replace(year=today.year + 3),
        #                                                  year=today.year + 2)
        # self.academic_year_3 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 3),
        #                                                  end_date=today.replace(year=today.year + 4),
        #                                                  year=today.year + 3)
        # self.academic_year_4 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 4),
        #                                                  end_date=today.replace(year=today.year + 5),
        #                                                  year=today.year + 4)
        # self.academic_year_5 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 5),
        #                                                  end_date=today.replace(year=today.year + 6),
        #                                                  year=today.year + 5)
        # self.academic_year_6 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 6),
        #                                                  end_date=today.replace(year=today.year + 7),
        #                                                  year=today.year + 6)
        self.current_academic_year = AcademicYearFactory(start_date=today,
                                                         end_date=today.replace(year=today.year+1),
                                                         year=today.year)
        # super(AcademicYear, self.academic_year_1).save()
        # super(AcademicYear, self.academic_year_2).save()
        # super(AcademicYear, self.academic_year_3).save()
        # super(AcademicYear, self.academic_year_4).save()
        # super(AcademicYear, self.academic_year_5).save()
        # super(AcademicYear, self.academic_year_6).save()
        # self.learning_container_yr = LearningContainerYearFactory(academic_year=self.current_academic_year)
        # self.learning_component_yr = LearningComponentYearFactory(learning_container_year=self.learning_container_yr)
        # self.organization = OrganizationFactory(type=organization_type.MAIN)
        self.country = CountryFactory()
        # self.entity = EntityFactory(country=self.country, organization=self.organization)
        # self.entity_2 = EntityFactory(country=self.country, organization=self.organization)
        # self.entity_3 = EntityFactory(country=self.country, organization=self.organization)
        # self.entity_container_yr = EntityContainerYearFactory(learning_container_year=self.learning_container_yr,
        #                                                       type=entity_container_year_link_type.REQUIREMENT_ENTITY,
        #                                                       entity=self.entity)
        # self.entity_container_yr_2 = EntityContainerYearFactory(learning_container_year=self.learning_container_yr,
        #                                                         type=entity_container_year_link_type.REQUIREMENT_ENTITY,
        #                                                         entity=self.entity_2)
        # self.entity_container_yr_3 = EntityContainerYearFactory(learning_container_year=self.learning_container_yr,
        #                                                         type=entity_container_year_link_type.REQUIREMENT_ENTITY,
        #                                                         entity=self.entity_3)
        # self.entity_version = EntityVersionFactory(entity=self.entity, entity_type=entity_type.SCHOOL, start_date=today,
        #                                            end_date=today.replace(year=today.year + 1))

        # self.campus = CampusFactory(organization=self.organization, is_administration=True, code="L")
        # self.language = LanguageFactory(code='FR')
        # self.a_superuser = SuperUserFactory()
        # self.client.force_login(self.a_superuser)

    def _prepare_context_learning_units_search(self):
        # Create a structure [Entity / Entity version]
        ssh_entity = EntityFactory(country=self.country)
        ssh_entity_v = EntityVersionFactory(acronym="SSH", end_date=None, entity=ssh_entity)

        agro_entity = EntityFactory(country=self.country)
        envi_entity = EntityFactory(country=self.country)
        ages_entity = EntityFactory(country=self.country)
        agro_entity_v = EntityVersionFactory(entity=agro_entity, parent=ssh_entity_v.entity, acronym="AGRO",
                                             end_date=None)
        envi_entity_v = EntityVersionFactory(entity=envi_entity, parent=agro_entity_v.entity, acronym="ENVI",
                                             end_date=None)
        ages_entity_v = EntityVersionFactory(entity=ages_entity, parent=agro_entity_v.entity, acronym="AGES",
                                             end_date=None)

        espo_entity = EntityFactory(country=self.country)
        drt_entity = EntityFactory(country=self.country)
        espo_entity_v = EntityVersionFactory(entity=espo_entity, parent=ssh_entity_v.entity, acronym="ESPO",
                                             end_date=None)
        drt_entity_v = EntityVersionFactory(entity=drt_entity, parent=ssh_entity_v.entity, acronym="DRT",
                                            end_date=None)

        # Create UE and put entity charge [AGRO]
        l_container_yr = LearningContainerYearFactory(acronym="LBIR1100", academic_year=self.current_academic_year,
                                                      container_type=learning_container_year_types.COURSE)
        EntityContainerYearFactory(learning_container_year=l_container_yr, entity=agro_entity_v.entity,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        LearningUnitYearFactory(acronym="LBIR1100", learning_container_year=l_container_yr,
                                academic_year=self.current_academic_year, subtype=learning_unit_year_subtypes.FULL)
        LearningUnitYearFactory(acronym="LBIR1100A", learning_container_year=l_container_yr,
                                academic_year=self.current_academic_year, subtype=learning_unit_year_subtypes.PARTIM)
        LearningUnitYearFactory(acronym="LBIR1100B", learning_container_year=l_container_yr,
                                academic_year=self.current_academic_year, subtype=learning_unit_year_subtypes.PARTIM)
        LearningUnitYearFactory(acronym="LBIR1100C", learning_container_year=l_container_yr,
                                academic_year=self.current_academic_year, subtype=learning_unit_year_subtypes.PARTIM,
                                status=False)

        # Create another UE and put entity charge [ENV]
        l_container_yr_2 = LearningContainerYearFactory(acronym="CHIM1200", academic_year=self.current_academic_year,
                                                        container_type=learning_container_year_types.COURSE)
        EntityContainerYearFactory(learning_container_year=l_container_yr_2, entity=envi_entity_v.entity,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        LearningUnitYearFactory(acronym="CHIM1200", learning_container_year=l_container_yr_2,
                                academic_year=self.current_academic_year, subtype=learning_unit_year_subtypes.FULL)

        # Create another UE and put entity charge [DRT]
        l_container_yr_3 = LearningContainerYearFactory(acronym="DRT1500", academic_year=self.current_academic_year,
                                                        container_type=learning_container_year_types.COURSE)
        EntityContainerYearFactory(learning_container_year=l_container_yr_3, entity=drt_entity_v.entity,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        LearningUnitYearFactory(acronym="DRT1500", learning_container_year=l_container_yr_3,
                                academic_year=self.current_academic_year, subtype=learning_unit_year_subtypes.FULL)
        LearningUnitYearFactory(acronym="DRT1500A", learning_container_year=l_container_yr_3,
                                academic_year=self.current_academic_year, subtype=learning_unit_year_subtypes.PARTIM)

        # Create another UE and put entity charge [ESPO]
        l_container_yr_4 = LearningContainerYearFactory(acronym="ESPO1500", academic_year=self.current_academic_year,
                                                        container_type=learning_container_year_types.DISSERTATION)
        EntityContainerYearFactory(learning_container_year=l_container_yr_4, entity=espo_entity_v.entity,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        LearningUnitYearFactory(acronym="ESPO1500", learning_container_year=l_container_yr_4,
                                academic_year=self.current_academic_year, subtype=learning_unit_year_subtypes.FULL)

        # Create another UE and put entity charge [AGES]
        l_container_yr_4 = LearningContainerYearFactory(acronym="AGES1500", academic_year=self.current_academic_year,
                                                        container_type=learning_container_year_types.MASTER_THESIS)
        EntityContainerYearFactory(learning_container_year=l_container_yr_4, entity=ages_entity_v.entity,
                                   type=entity_container_year_link_type.REQUIREMENT_ENTITY)
        LearningUnitYearFactory(acronym="AGES1500", learning_container_year=l_container_yr_4,
                                academic_year=self.current_academic_year, subtype=None)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units_search(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        build_future_academic_years()
        request_factory = RequestFactory()
        request = request_factory.get(reverse('learning_units'))
        request.user = mock.Mock()

        from base.views.learning_unit_search import learning_units

        learning_units(request)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(context['academic_years'].count(), 7)
        self.assertEqual(context['current_academic_year'], self.current_academic_year)
        self.assertEqual(len(context['types']),
                         len(learning_unit_year_subtypes.LEARNING_UNIT_YEAR_SUBTYPES))
        self.assertEqual(len(context['container_types']),
                         len(learning_container_year_types.LEARNING_CONTAINER_YEAR_TYPES))
        self.assertTrue(context['experimental_phase'])
        self.assertIsNone(context['learning_units'])

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units_search_with_acronym_filtering(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        self._prepare_context_learning_units_search()
        request_factory = RequestFactory()
        filter_data = {
            'academic_year_id': self.current_academic_year.id,
            'status': True,
            'acronym': 'LBIR'
        }
        request = request_factory.get(reverse('learning_units'), data=filter_data)
        request.user = mock.Mock()
        from base.views.learning_unit_search import learning_units
        learning_units(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(len(context['learning_units']), 3)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units_search_by_acronym_with_valid_regex(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        self._prepare_context_learning_units_search()
        request_factory = RequestFactory()
        filter_data = {
            'academic_year_id': self.current_academic_year.id,
            'status': True,
            'acronym': '^DRT.+A'
        }
        request = request_factory.get(reverse('learning_units'), data=filter_data)
        request.user = mock.Mock()
        from base.views.learning_unit_search import learning_units
        learning_units(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(len(context['learning_units']), 1)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units_search_by_acronym_with_invalid_regex(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        self._prepare_context_learning_units_search()
        request_factory = RequestFactory()
        filter_data = {
            'academic_year_id': self.current_academic_year.id,
            'status': True,
            'acronym': '^LB(+)2+'
        }
        request = request_factory.get(reverse('learning_units'), data=filter_data)
        request.user = mock.Mock()
        from base.views.learning_unit_search import learning_units
        learning_units(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(context['form'].errors['acronym'], [_('LU_ERRORS_INVALID_REGEX_SYNTAX')])

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units_search_with_requirement_entity(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        self._prepare_context_learning_units_search()
        request_factory = RequestFactory()
        filter_data = {
            'academic_year_id': self.current_academic_year.id,
            'requirement_entity_acronym': 'ENVI'
        }
        request = request_factory.get(reverse('learning_units'), data=filter_data)
        request.user = mock.Mock()
        from base.views.learning_unit_search import learning_units
        learning_units(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(len(context['learning_units']), 1)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units_search_with_requirement_entity_and_subord(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        self._prepare_context_learning_units_search()
        request_factory = RequestFactory()
        filter_data = {
            'academic_year_id': self.current_academic_year.id,
            'requirement_entity_acronym': 'AGRO',
            'with_entity_subordinated': True
        }
        request = request_factory.get(reverse('learning_units'), data=filter_data)
        request.user = mock.Mock()
        from base.views.learning_unit_search import learning_units
        learning_units(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(len(context['learning_units']), 6)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    def test_learning_units_search_with_service_course(self, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        self._prepare_context_learning_units_search()
        request_factory = RequestFactory()
        filter_data = {
            'academic_year_id': self.current_academic_year.id,
            'requirement_entity_acronym': 'AGRO',
            'with_entity_subordinated': True
        }
        from base.views.learning_unit_search import learning_units_service_course

        request = request_factory.get(reverse(learning_units_service_course), data=filter_data)
        request.user = mock.Mock()
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        learning_units_service_course(request)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'learning_units.html')
        self.assertEqual(len(context['learning_units']), 0)

    @mock.patch("base.models.learning_unit_year.count_search_results")
    def test_error_message_case_too_many_results_to_show(self, mock_count):
        self.a_superuser = SuperUserFactory()
        self.client.force_login(self.a_superuser)
        mock_count.return_value = learning_unit_search.MAX_RECORDS + 1
        response = self.client.get(reverse('learning_units'), {'academic_year_id': self.current_academic_year.id})
        messages = list(response.context['messages'])
        self.assertEqual(messages[0].message, _('too_many_results'))