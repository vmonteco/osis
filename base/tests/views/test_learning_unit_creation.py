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
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase
from base.forms.learning_unit_creation import CreateLearningUnitYearForm
from base.models.academic_year import AcademicYear
from base.models.enums import organization_type, entity_type
from base.models.enums.internship_subtypes import TEACHING_INTERNSHIP
from base.models.enums.learning_container_year_types import COURSE
from base.models.enums.learning_unit_periodicity import ANNUAL
from base.models.enums.learning_unit_year_subtypes import FULL
from base.models.enums.learning_unit_year_session import SESSION_P23
from base.models.learning_unit import LearningUnit
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.campus import CampusFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.organization import OrganizationFactory
from base.tests.factories.person import PersonFactory
from reference.tests.factories.language import LanguageFactory


OK = 200
ACCESS_DENIED = 401


class LearningUnitCreate(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.url = reverse('learning_unit_create', args=[2015])
        self.language = LanguageFactory(code='FR')

        self.client.force_login(self.person.user)

    def test_with_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        from django.utils.encoding import uri_to_iri
        self.assertEqual(uri_to_iri(uri_to_iri(response.url)), '/login/?next={}'.format(self.url))
        self.assertEqual(response.status_code, 302)

    def test_when_user_has_not_permission(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_when_user_has_permission(self):
        content_type = ContentType.objects.get_for_model(LearningUnit)
        permission = Permission.objects.get(codename="can_access_learningunit",
                                            content_type=content_type)
        self.person.user.user_permissions.add(permission)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'learning_unit/learning_unit_form.html')

        self.assertIsInstance(response.context['form'],  CreateLearningUnitYearForm)


class LearningUnitYearAdd(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        content_type = ContentType.objects.get_for_model(LearningUnit)
        permission = Permission.objects.get(codename="can_access_learningunit",
                                            content_type=content_type)
        self.person.user.user_permissions.add(permission)
        self.url = reverse('learning_unit_year_add')

        self.client.force_login(self.person.user)

    def test_with_user_not_logged(self):
        self.client.logout()
        response = self.client.post(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_when_user_has_not_permission(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_when_get_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(response, 'method_not_allowed.html')

    def test_when_empty_form_data(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'learning_unit/learning_unit_form.html')

        self.assertIsInstance(response.context['form'], CreateLearningUnitYearForm)

    def test_when_valid_form_data(self):
        today = datetime.date.today()
        academic_year_1 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 1),
                                                    end_date=today.replace(year=today.year + 2),
                                                    year=today.year + 1)
        academic_year_2 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 2),
                                                    end_date=today.replace(year=today.year + 3),
                                                    year=today.year + 2)
        academic_year_3 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 3),
                                                    end_date=today.replace(year=today.year + 4),
                                                    year=today.year + 3)
        academic_year_4 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 4),
                                                    end_date=today.replace(year=today.year + 5),
                                                    year=today.year + 4)
        academic_year_5 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 5),
                                                    end_date=today.replace(year=today.year + 6),
                                                    year=today.year + 5)
        academic_year_6 = AcademicYearFactory.build(start_date=today.replace(year=today.year + 6),
                                                    end_date=today.replace(year=today.year + 7),
                                                    year=today.year + 6)
        current_academic_year = AcademicYearFactory(start_date=today,
                                                    end_date=today.replace(year=today.year + 1),
                                                    year=today.year)
        super(AcademicYear, academic_year_1).save()
        super(AcademicYear, academic_year_2).save()
        super(AcademicYear, academic_year_3).save()
        super(AcademicYear, academic_year_4).save()
        super(AcademicYear, academic_year_5).save()
        super(AcademicYear, academic_year_6).save()

        organization = OrganizationFactory(type=organization_type.MAIN)
        campus = CampusFactory(organization=organization)
        entity = EntityFactory(organization=organization)
        entity_version = EntityVersionFactory(entity=entity, entity_type=entity_type.SCHOOL, start_date=today,
                                              end_date=today.replace(year=today.year + 1))
        language = LanguageFactory()

        form_data = {
            "first_letter": "L",
            "acronym": "TAU2000",
            "learning_container_year_type": COURSE,
            "academic_year": current_academic_year.id,
            "status": True,
            "periodicity": ANNUAL,
            "credits": "5",
            "campus": campus.id,
            "internship_subtype": TEACHING_INTERNSHIP,
            "title": "LAW",
            "title_english": "LAW",
            "requirement_entity": entity_version.id,
            "subtype": FULL,
            "language": language.id,
            "session": SESSION_P23,
            "faculty_remark": "faculty remark",
            "other_remark": "other remark"
        }

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)
