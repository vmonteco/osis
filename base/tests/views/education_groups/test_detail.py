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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from base.tests.factories.education_group_achievement import EducationGroupAchievementFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group_element_year import GroupElementYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from base.views.education_groups.detail import CMS_LABEL_CERTIFICAT_AIM, CMS_LABEL_ADDITIONAL_INFORMATION
from cms.enums import entity_name
from cms.tests.factories.translated_text import TranslatedTextFactory
from reference.models.language import FR_CODE_LANGUAGE, EN_CODE_LANGUAGE
from reference.tests.factories.language import LanguageFactory


class TestDetail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = PersonFactory()
        cls.education_group_year_1 = EducationGroupYearFactory(title_english="")
        cls.education_group_year_2 = EducationGroupYearFactory(title_english="")
        cls.education_group_year_3 = EducationGroupYearFactory(title_english="")
        cls.learning_unit_year_1 = LearningUnitYearFactory(specific_title_english="")
        cls.learning_unit_year_2 = LearningUnitYearFactory(specific_title_english="")
        cls.learning_component_year_1 = LearningComponentYearFactory(
            learning_container_year=cls.learning_unit_year_1.learning_container_year, hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10)
        cls.learning_component_year_2 = LearningComponentYearFactory(
            learning_container_year=cls.learning_unit_year_1.learning_container_year, hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10)
        cls.learning_unit_component_1 = LearningUnitComponentFactory(
            learning_component_year=cls.learning_component_year_1,
            learning_unit_year=cls.learning_unit_year_1)
        cls.learning_unit_component_2 = LearningUnitComponentFactory(
            learning_component_year=cls.learning_component_year_2,
            learning_unit_year=cls.learning_unit_year_1)
        cls.group_element_year_1 = GroupElementYearFactory(parent=cls.education_group_year_1,
                                                           child_branch=cls.education_group_year_2)
        cls.group_element_year_2 = GroupElementYearFactory(parent=cls.education_group_year_2,
                                                           child_branch=None,
                                                           child_leaf=cls.learning_unit_year_1)
        cls.group_element_year_3 = GroupElementYearFactory(parent=cls.education_group_year_1,
                                                           child_branch=cls.education_group_year_3)
        cls.group_element_year_4 = GroupElementYearFactory(parent=cls.education_group_year_3,
                                                           child_branch=None,
                                                           child_leaf=cls.learning_unit_year_2)
        cls.user = UserFactory()
        cls.person = PersonFactory(user=cls.user)
        cls.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))

        cls.url = reverse(
            "education_group_utilization",
            args=[
                cls.education_group_year_2.id,
                cls.education_group_year_2.id,
            ]
        )

    def test_education_group_using_template_use(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'education_group/tab_utilization.html')

    def test_education_group_using_check_parent_list_with_group(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(len(response.context_data['group_element_years']), 1)
        self.assertTemplateUsed(response, 'education_group/tab_utilization.html')


class TestContent(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.education_group_year_1 = EducationGroupYearFactory()
        self.education_group_year_2 = EducationGroupYearFactory()
        self.education_group_year_3 = EducationGroupYearFactory()
        self.learning_unit_year_1 = LearningUnitYearFactory()

        self.learning_component_year_1 = LearningComponentYearFactory(
            learning_container_year=self.learning_unit_year_1.learning_container_year,
            hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10
        )

        self.learning_component_year_2 = LearningComponentYearFactory(
            learning_container_year=self.learning_unit_year_1.learning_container_year,
            hourly_volume_partial_q1=10,
            hourly_volume_partial_q2=10
        )

        self.learning_unit_component_1 = LearningUnitComponentFactory(
            learning_component_year=self.learning_component_year_1,
            learning_unit_year=self.learning_unit_year_1
        )

        self.learning_unit_component_2 = LearningUnitComponentFactory(
            learning_component_year=self.learning_component_year_2,
            learning_unit_year=self.learning_unit_year_1
        )

        self.learning_unit_year_without_container = LearningUnitYearFactory(
            learning_container_year=None
        )

        self.group_element_year_1 = GroupElementYearFactory(parent=self.education_group_year_1,
                                                            child_branch=self.education_group_year_2)

        self.group_element_year_2 = GroupElementYearFactory(parent=self.education_group_year_1,
                                                            child_branch=None,
                                                            child_leaf=self.learning_unit_year_1)

        self.group_element_year_3 = GroupElementYearFactory(parent=self.education_group_year_1,
                                                            child_branch=self.education_group_year_3)

        self.group_element_year_without_container = GroupElementYearFactory(
            parent=self.education_group_year_1,
            child_branch=None,
            child_leaf=self.learning_unit_year_without_container
        )

        self.user = UserFactory()
        self.person = PersonFactory(user=self.user)
        self.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))

        self.url = reverse(
            "education_group_content",
            args=[
                self.education_group_year_1.id,
                self.education_group_year_1.id,
            ]
        )
        self.client.force_login(self.user)

    def test_context(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "education_group/tab_content.html")

        geys = response.context["group_element_years"]
        self.assertIn(self.group_element_year_1, geys)
        self.assertIn(self.group_element_year_2, geys)
        self.assertIn(self.group_element_year_3, geys)
        self.assertNotIn(self.group_element_year_without_container, geys)


class TestEducationGroupSkillsAchievements(TestCase):
    def setUp(self):

        self.education_group_year = EducationGroupYearFactory()

        self.user = UserFactory()
        self.person = PersonFactory(user=self.user)
        self.user.user_permissions.add(Permission.objects.get(codename="can_access_education_group"))
        self.client.force_login(self.user)

    def _call_url_as_http_get(self):
        response = self.client.get(
            reverse("education_group_skills_achievements",
                    args=[self.education_group_year.pk, self.education_group_year.pk])
        )
        self.assertEqual(response.status_code, 200)
        return response

    def test_get__achievements(self):
        achievement = EducationGroupAchievementFactory(education_group_year=self.education_group_year)

        response = self._call_url_as_http_get()

        self.assertEqual(
            response.context["education_group_achievements"][0], achievement
        )

    def test_get__certificate_aim(self):
        certificate_aim_french = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.id,
            text_label__label=CMS_LABEL_CERTIFICAT_AIM,
            language=settings.LANGUAGE_CODE_FR,
        )
        certificate_aim_english = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.id,
            text_label__label=CMS_LABEL_CERTIFICAT_AIM,
            language=settings.LANGUAGE_CODE_EN,
        )
        response = self._call_url_as_http_get()
        self.assertEqual(
            response.context["certificate_aim"][0], certificate_aim_french
        )
        self.assertEqual(
            response.context["certificate_aim"][1], certificate_aim_english
        )

    def test_get__additional_informations(self):
        additional_infos_french = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.id,
            text_label__label=CMS_LABEL_ADDITIONAL_INFORMATION,
            language=settings.LANGUAGE_CODE_FR,
        )
        additional_infos_english = TranslatedTextFactory(
            entity=entity_name.OFFER_YEAR,
            reference=self.education_group_year.id,
            text_label__label=CMS_LABEL_ADDITIONAL_INFORMATION,
            language=settings.LANGUAGE_CODE_EN,
        )
        response = self._call_url_as_http_get()
        self.assertEqual(
            response.context["additional_informations"][0], additional_infos_french
        )
        self.assertEqual(
            response.context["additional_informations"][1], additional_infos_english
        )
