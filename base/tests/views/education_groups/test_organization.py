##############################################################################
#
#    OSIS stands for Open Student Information System. It"s an application
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
import datetime
from unittest import mock

from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base import utils
from base.forms.education_groups import EducationGroupFilter
from base.models.enums import education_group_categories
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from base.views.education_groups import search
from django.contrib.messages.storage.fallback import FallbackStorage
FILTER_DATA = {"acronym": "LBIR", "title": "dummy filter"}
from base.forms.education_group.organization import OrganizationEditForm
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.education_group_organization import EducationGroupOrganizationFactory
from base.tests.factories.entity import EntityFactory
from reference.tests.factories.country import CountryFactory
from base.models.education_group_organization import EducationGroupOrganization

class TestOrganizationView(TestCase):

    def setUp(self):
        self.user = UserFactory()

        self.client.force_login(self.user)

        self.person = PersonFactory(user=self.user)
        self.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))


        today = datetime.date.today()
        self.academic_year = AcademicYearFactory(start_date=today, end_date=today.replace(year=today.year + 1),
                                                year=today.year)
        self.type_training = EducationGroupTypeFactory(category=education_group_categories.TRAINING)
        oph_entity = EntityFactory()

        self.education_group_arke2a = EducationGroupYearFactory(
            acronym='ARKE2A', academic_year=self.academic_year,
            education_group_type=self.type_training,
            management_entity=oph_entity
        )
        self.organization = OrganizationFactory()
        # self.country_be = CountryFactory()
        # self.entity = EntityFactory(country=self.country_be,
        #                             organization=self.organization)
        # root_entity_version = EntityVersionFactory(entity=self.entity,
        #                                            title="ROOT_V",
        #                                            start_date=self.academic_year.start_date,
        #                                            end_date=None,
        #                                            parent=None)
        # print('---------------------------------------------------')
        # print(root_entity_version.title)


    @mock.patch('base.views.layout.render')
    def test_create_get(self, mock_render):
        simple_url = reverse('education_group_read', kwargs={
            'root_id': self.education_group_arke2a.id,
            'education_group_year_id':self.education_group_arke2a.id,
        })

        request_factory = RequestFactory()
        request = request_factory.get(simple_url)

        request.user = self.user

        from base.views.education_groups.coorganization import create
        create(request, root_id= self.education_group_arke2a.id, education_group_year_id= self.education_group_arke2a.id)
        self.assertTrue(mock_render.called)
        request, template, context = mock_render.call_args[0]

        self.assertEqual(template, 'education_group/organization_edit.html')
        self.assertIsInstance(context['form'], OrganizationEditForm)
        self.assertEqual(context['education_group_year'], self.education_group_arke2a)
        self.assertEqual(context['root_id'], self.education_group_arke2a.id)
        self.assertTrue(context['create'])


#     @mock.patch('base.views.layout.render')
#     def test_create_post(self, mock_render):
#         simple_url = reverse('education_group_read', kwargs={
#             'root_id': self.education_group_arke2a.id,
#             'education_group_year_id': self.education_group_arke2a.id,
#         })
#
#         request_factory = RequestFactory()
#         request = request_factory.post(simple_url)
#
#         request.user = self.user
#         data = {
#
#         "organization": self.organization.id,
#         "'diploma":  "UNIQUE"}
#
#
# # <QueryDict: {'csrfmiddlewaretoken': ['XtWaF1jcAAHm5J8ssxtz7vYgnc1PfHmldAVnCscNZ7vqLWIqROq4fTgTgUwtYfsE'], 'country': ['88'], 'organization': ['76'], 'all_students': ['on'], 'enrollment_place': ['on'], 'diploma': ['UNIQUE'], 'is_producing_cerfificate': ['on'], 'is_producing_annexe': ['on']}>
#         response = self.client.post(reverse('coorganization_create', kwargs={
#                 'root_id': self.education_group_arke2a.id,
#                 'education_group_year_id': self.education_group_arke2a.id
#             }), data=data)
#         self.assertEqual(response.status_code, HTTPStatus.FOUND)


    def test_education_group_organization_delete(self):
        education_group_organization_to_delete = EducationGroupOrganizationFactory()
        root_id=self.education_group_arke2a.pk

        http_referer = reverse('education_group_read', args=[
            root_id,
            self.education_group_arke2a.id
        ])

        response = self.client.post(reverse('coorganization_delete', args=[root_id,self.education_group_arke2a.id]),
                                    data={'coorganization_id_to_delete': education_group_organization_to_delete.id})

        self.assertRedirects(response, http_referer)
        with self.assertRaises(EducationGroupOrganization.DoesNotExist):
            education_group_organization_to_delete.refresh_from_db()


    # def test_learning_achievement_save(self):
    #     root_id=self.education_group_arke2a.pk
    #     education_group_organization = EducationGroupOrganizationFactory(education_group_year=self.education_group_arke2a)
    #     response = self.client.post(reverse('coorganization_create',
    #                                         kwargs={'root_id': root_id,
    #                                                 'education_group_year_id': self.education_group_arke2a.id}),
    #                                 data={'organization': self.organization, 'diploma': 'UNIQUE'})
    #
    #     # expected_redirection = reverse("learning_unit_specifications",
    #     #                                kwargs={'learning_unit_year_id': self.learning_unit_year.id}) + "{}{}".format(
    #     #     HTML_ANCHOR, learning_achievement.id)
    #     # self.assertRedirects(response, expected_redirection, fetch_redirect_response=False)
