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
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from base.forms.learning_unit_creation import CreateLearningUnitYearForm
from base.models import learning_unit_component
from base.models import learning_unit_component_class
from base.models.academic_year import AcademicYear
from base.models.enums import organization_type, entity_type
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.internship_subtypes import TEACHING_INTERNSHIP
from base.models.enums.learning_container_year_types import COURSE
from base.models.enums.learning_unit_periodicity import ANNUAL
from base.models.enums.learning_unit_year_subtypes import FULL
from base.models.enums.learning_unit_year_session import SESSION_P23
from base.models.learning_unit_year import LearningUnitYear
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.learning_unit_component_class import LearningUnitComponentClassFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_class_year import LearningClassYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.models.enums import entity_container_year_link_type
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.user import SuperUserFactory
from django.utils.translation import ugettext_lazy as _
from reference.tests.factories.country import CountryFactory
from reference.tests.factories.language import LanguageFactory


class LearningUnitViewTestCase(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.academic_year_1 = AcademicYearFactory.build(start_date=today.replace(year=today.year+1),
                                                         end_date=today.replace(year=today.year+2),
                                                         year=today.year+1)
        self.academic_year_2 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 2),
                                                         end_date=today.replace(year=today.year + 3),
                                                         year=today.year + 2)
        self.academic_year_3 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 3),
                                                         end_date=today.replace(year=today.year + 4),
                                                         year=today.year + 3)
        self.academic_year_4 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 4),
                                                         end_date=today.replace(year=today.year + 5),
                                                         year=today.year + 4)
        self.academic_year_5 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 5),
                                                         end_date=today.replace(year=today.year + 6),
                                                         year=today.year + 5)
        self.academic_year_6 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 6),
                                                         end_date=today.replace(year=today.year + 7),
                                                         year=today.year + 6)
        self.current_academic_year = AcademicYearFactory(start_date=today,
                                                         end_date=today.replace(year=today.year+1),
                                                         year=today.year)
        super(AcademicYear, self.academic_year_1).save()
        super(AcademicYear, self.academic_year_2).save()
        super(AcademicYear, self.academic_year_3).save()
        super(AcademicYear, self.academic_year_4).save()
        super(AcademicYear, self.academic_year_5).save()
        super(AcademicYear, self.academic_year_6).save()
        self.learning_container_yr = LearningContainerYearFactory(academic_year=self.current_academic_year)
        self.learning_component_yr = LearningComponentYearFactory(learning_container_year=self.learning_container_yr)
        self.organization = OrganizationFactory(type=organization_type.MAIN)
        self.country = CountryFactory()
        self.entity = EntityFactory(country=self.country, organization=self.organization)
        self.entity_2 = EntityFactory(country=self.country, organization=self.organization)
        self.entity_3 = EntityFactory(country=self.country, organization=self.organization)
        self.entity_container_yr = EntityContainerYearFactory(learning_container_year=self.learning_container_yr,
                                                              type=entity_container_year_link_type.REQUIREMENT_ENTITY,
                                                              entity=self.entity)
        self.entity_container_yr_2 = EntityContainerYearFactory(learning_container_year=self.learning_container_yr,
                                                              type=entity_container_year_link_type.REQUIREMENT_ENTITY,
                                                              entity=self.entity_2)
        self.entity_container_yr_3 = EntityContainerYearFactory(learning_container_year=self.learning_container_yr,
                                                              type=entity_container_year_link_type.REQUIREMENT_ENTITY,
                                                              entity=self.entity_3)
        self.entity_version = EntityVersionFactory(entity=self.entity, entity_type=entity_type.SCHOOL, start_date=today,
                                                   end_date=today.replace(year=today.year + 1))

        self.campus = CampusFactory(organization=self.organization, is_administration=True, code="L")
        self.language = LanguageFactory(code='FR')
        self.a_superuser = SuperUserFactory()
        self.client.force_login(self.a_superuser)

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.program_manager.is_program_manager')
    def test_get_partims_identification_tabs(self, mock_program_manager, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        mock_program_manager.return_value = True

        learning_unit_container_year = LearningContainerYearFactory(
            academic_year=self.current_academic_year
        )
        learning_unit_year = LearningUnitYearFactory(
            acronym="LCHIM1210",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.FULL,
            academic_year=self.current_academic_year
        )
        LearningUnitYearFactory(
            acronym="LCHIM1210A",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.PARTIM,
            academic_year=self.current_academic_year
        )
        LearningUnitYearFactory(
            acronym="LCHIM1210B",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.PARTIM,
            academic_year=self.current_academic_year
        )
        LearningUnitYearFactory(
            acronym="LCHIM1210F",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.PARTIM,
            academic_year=self.current_academic_year
        )

        request_factory = RequestFactory()
        request = request_factory.get(reverse('learning_unit', args=[learning_unit_year.id]))
        request.user = mock.Mock()

        from base.views.learning_unit import learning_unit_identification

        learning_unit_identification(request, learning_unit_year.id)

        self.assertTrue(mock_render.called)

        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'learning_unit/identification.html')
        self.assertEqual(len(context['learning_container_year_partims']), 3)

    def test_component_save(self):
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   learning_container_year=self.learning_container_yr)
        learning_unit_compnt = LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                                            learning_component_year=self.learning_component_yr)
        url = reverse('learning_unit_component_edit', args=[learning_unit_yr.id])
        qs = 'learning_component_year_id={}'.format(self.learning_component_yr.id)

        response = self.client.post('{}?{}'.format(url, qs), data={"used_by": "on"})
        self.learning_component_yr.refresh_from_db()
        self.assertEqual(response.status_code, 302)


    def test_component_save_delete_link(self):
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   learning_container_year=self.learning_container_yr)
        learning_unit_compnt = LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                                            learning_component_year=self.learning_component_yr)
        url = reverse('learning_unit_component_edit', args=[learning_unit_yr.id])
        qs = 'learning_component_year_id={}'.format(self.learning_component_yr.id)

        response = self.client.post('{}?{}'.format(url, qs), data={"planned_classes": "1"})
        self.assertRaises(ObjectDoesNotExist, learning_unit_component.LearningUnitComponent.objects.filter(pk=learning_unit_compnt.id).first())

    def test_component_save_create_link(self):
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   learning_container_year=self.learning_container_yr)
        url = reverse('learning_unit_component_edit', args=[learning_unit_yr.id])
        qs = 'learning_component_year_id={}'.format(self.learning_component_yr.id)

        response = self.client.post('{}?{}'.format(url, qs), data={"planned_classes": "1", "used_by": "on"})

        self.assertTrue(learning_unit_component.find_by_learning_component_year(self.learning_component_yr).exists())

    def test_class_save(self):
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   learning_container_year=self.learning_container_yr)
        learning_unit_compnt = LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                                            learning_component_year=self.learning_component_yr)
        learning_class_yr = LearningClassYearFactory(learning_component_year=self.learning_component_yr)

        response = self.client.post('{}?{}&{}'.format(reverse('learning_class_year_edit', args=[learning_unit_yr.id]),
                                                      'learning_component_year_id={}'.format(self.learning_component_yr.id),
                                                      'learning_class_year_id={}'.format(learning_class_yr.id)),
                                    data={"used_by": "on"})
        self.learning_component_yr.refresh_from_db()
        self.assertEqual(response.status_code, 302)

    def test_class_save_create_link(self):
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   learning_container_year=self.learning_container_yr)
        learning_unit_compnt = LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                                            learning_component_year=self.learning_component_yr)
        learning_class_yr = LearningClassYearFactory(learning_component_year=self.learning_component_yr)

        response = self.client.post('{}?{}&{}'.format(reverse('learning_class_year_edit', args=[learning_unit_yr.id]),
                                                      'learning_component_year_id={}'.format(self.learning_component_yr.id),
                                                      'learning_class_year_id={}'.format(learning_class_yr.id)),
                                    data={"used_by": "on"})

        self.assertTrue(learning_unit_component_class.search(learning_unit_compnt, learning_class_yr).exists())

    def test_class_save_delete_link(self):
        learning_unit_yr = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                   learning_container_year=self.learning_container_yr)
        learning_unit_compnt = LearningUnitComponentFactory(learning_unit_year=learning_unit_yr,
                                                            learning_component_year=self.learning_component_yr)
        learning_class_yr = LearningClassYearFactory(learning_component_year=self.learning_component_yr)
        a_link = LearningUnitComponentClassFactory(learning_unit_component=learning_unit_compnt,
                                                   learning_class_year=learning_class_yr)

        response = self.client.post('{}?{}&{}'.format(reverse('learning_class_year_edit', args=[learning_unit_yr.id]),
                                                      'learning_component_year_id={}'.format(self.learning_component_yr.id),
                                                      'learning_class_year_id={}'.format(learning_class_yr.id)), data={})

        self.assertRaises(ObjectDoesNotExist, learning_unit_component_class.LearningUnitComponentClass.objects.filter(pk=a_link.id).first())

    def get_base_form_data(self):
        return {"first_letter": "L",
                "acronym": "TAU2000",
                "learning_container_year_type": COURSE,
                "academic_year": self.current_academic_year.id,
                "status": True,
                "periodicity": ANNUAL,
                "credits": "5",
                "campus": self.campus.id,
                "internship_subtype": TEACHING_INTERNSHIP,
                "title": "LAW",
                "title_english": "LAW",
                "requirement_entity": self.entity_version.id,
                "allocation_entity": self.entity_version.id,
                "additional_entity_1": self.entity_version.id,
                "additional_entity_2": self.entity_version.id,
                "subtype": FULL,
                "language": self.language.id,
                "session": SESSION_P23,
                "faculty_remark": "faculty remark",
                "other_remark": "other remark"}

    def get_valid_data(self):
        return self.get_base_form_data()

    def get_faulty_acronym(self):
        faultydict = dict(self.get_valid_data())
        faultydict["acronym"] = "TA200"
        return faultydict

    def get_empty_acronym(self):
        faultyDict = dict(self.get_valid_data())
        faultyDict["acronym"] = ""
        return faultyDict

    def test_learning_unit_year_form(self):
        form = CreateLearningUnitYearForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid(), form.errors)
        url = reverse('learning_unit_year_add')
        response = self.client.post(url, data=self.get_base_form_data())
        self.assertEqual(response.status_code, 302)
        count_learning_unit_year = LearningUnitYear.objects.all().count()
        self.assertEqual(count_learning_unit_year, 6)

    def test_learning_unit_acronym_form(self):
        form = CreateLearningUnitYearForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid(), form.errors)

        form = CreateLearningUnitYearForm(data=self.get_empty_acronym())
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual(form.errors['acronym'], [_('This field is required.')])

        form = CreateLearningUnitYearForm(data=self.get_faulty_acronym())
        self.assertFalse(form.is_valid(), form.errors)
        self.assertEqual(form.errors['acronym'], [_('invalid_acronym')])

    def test_learning_unit_check_acronym(self):
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        url = reverse('check_acronym')
        get_data = {'acronym': 'goodacronym', 'year_id': self.academic_year_1.id}
        response = self.client.get(url, get_data, **kwargs)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content , encoding='utf8'),
            {'valid': True,
             'existing_acronym': False,
             'existed_acronym': False,
             'last_using': ""}
        )

        learning_unit_container_year = LearningContainerYearFactory(
            academic_year=self.current_academic_year
        )
        learning_unit_year = LearningUnitYearFactory(
            acronym="LCHIM1210",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.FULL,
            academic_year=self.current_academic_year
        )
        learning_unit_year.save()

        get_data = {'acronym': 'LCHIM1210', 'year_id': self.current_academic_year.id}
        response = self.client.get(url, get_data, **kwargs)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content , encoding='utf8'),
            {'valid': False,
             'existing_acronym': True,
             'existed_acronym': False,
             'last_using': ""}
        )

        learning_unit_year = LearningUnitYearFactory(
            acronym="LCHIM1211",
            learning_container_year=learning_unit_container_year,
            subtype=learning_unit_year_subtypes.FULL,
            academic_year=self.current_academic_year
        )
        learning_unit_year.save()

        get_data = {'acronym': 'LCHIM1211', 'year_id': self.academic_year_6.id}
        response = self.client.get(url, get_data, **kwargs)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content , encoding='utf8'),
            {'valid': True,
             'existing_acronym': False,
             'existed_acronym': True,
             'last_using': str(self.current_academic_year)}
        )

    def _get_volumes_data(self, learning_units_year):
        if not isinstance(learning_units_year, list):
            learning_units_year = [learning_units_year]
        data = {}
        for learning_unit_year in learning_units_year:
            data['VOLUME_TOTAL_REQUIREMENT_ENTITIES_{}_{}'.format(learning_unit_year.id, self.learning_component_yr.id)] = [60]
            data['VOLUME_Q1_{}_{}'.format(learning_unit_year.id, self.learning_component_yr.id)] = [10]
            data['VOLUME_Q2_{}_{}'.format(learning_unit_year.id, self.learning_component_yr.id)] = [20]
            data['VOLUME_TOTAL_{}_{}'.format(learning_unit_year.id, self.learning_component_yr.id)] = [30]
            data['PLANNED_CLASSES_{}_{}'.format(learning_unit_year.id, self.learning_component_yr.id)] = [2]
        return data

    @mock.patch('django.contrib.auth.decorators')
    @mock.patch('base.views.layout.render')
    @mock.patch('base.models.program_manager.is_program_manager')
    def test_get_learning_unit_volumes_management(self, mock_program_manager, mock_render, mock_decorators):
        mock_decorators.login_required = lambda x: x
        mock_decorators.permission_required = lambda *args, **kwargs: lambda func: func
        mock_program_manager.return_value = True

        learning_unit_year = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                     learning_container_year=self.learning_container_yr)
        learning_unit_year.save()

        request_factory = RequestFactory()
        url = reverse("learning_unit_volumes_management", args=[learning_unit_year.id])
        # GET request
        request = request_factory.get(url)
        request.user = mock.Mock()
        from base.views.learning_unit import learning_unit_volumes_management
        learning_unit_volumes_management(request, learning_unit_year.id)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]
        self.assertEqual(template, 'learning_unit/volumes_management.html')
        self.assertEqual(context['tab_active'], 'components')

        # POST request
        request = request_factory.post(url, self._get_volumes_data([learning_unit_year]))
        request.user = mock.Mock()
        learning_unit_volumes_management(request, learning_unit_year.id)
        self.assertTrue(mock_render.called)

    def test_volumes_validation(self):
        learning_unit_year = LearningUnitYearFactory(academic_year=self.current_academic_year,
                                                     learning_container_year=self.learning_container_yr)
        learning_unit_year.save()

        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        url = reverse("volumes_validation", args=[learning_unit_year.id])

        data = self._get_volumes_data(learning_unit_year)
        #TODO inject wrong data
        response = self.client.get(url, data, **kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'errors': [],
             }
        )
