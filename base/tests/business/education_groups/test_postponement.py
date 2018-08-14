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
from django.forms import model_to_dict
from django.test import TestCase

from base.business.education_groups.postponement import EDUCATION_GROUP_MAX_POSTPONE_YEARS, _compute_end_year, \
    _model_to_dict, _postpone_education_group_year, start, _get_start_education_group_year
from base.models.education_group_year import EducationGroupYear
from base.models.education_group_year_domain import EducationGroupYearDomain
from base.models.enums import entity_type
from base.models.enums import organization_type
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.business.learning_units import GenerateAcademicYear
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_language import EducationGroupLanguageFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.education_group_year_domain import EducationGroupYearDomainFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory


class EducationGroupPostponementContextMixin(TestCase):
    """This mixin is used in this test file in order to setup an environment for testing EGY POSTPONEMENT"""
    def setUp(self):
        # Create several academic year
        self.current_academic_year = create_current_academic_year()
        self.generated_ac_years = GenerateAcademicYear(self.current_academic_year.year + 1,
                                                       self.current_academic_year.year + 10)
        # Create small entities
        self.entity = EntityFactory(organization__type=organization_type.MAIN)
        self.entity_version = EntityVersionFactory(
            entity=self.entity,
            entity_type=entity_type.SECTOR
        )

        self.education_group_year = EducationGroupYearFactory(
            management_entity=self.entity,
            administration_entity=self.entity,
            academic_year=self.current_academic_year
        )
        # Create a group language
        EducationGroupLanguageFactory(education_group_year=self.education_group_year)

        # Create two secondary domains
        EducationGroupYearDomainFactory(education_group_year=self.education_group_year)
        EducationGroupYearDomainFactory(education_group_year=self.education_group_year)

    def assertPostponementEquals(self, education_group_year, education_group_year_postponed):
        # Check all attribute without m2m / unreleveant fields
        fields_to_exclude = ['id', 'external_id', 'academic_year', 'languages', 'secondary_domains']
        egy_dict = model_to_dict(
            education_group_year,
            exclude=fields_to_exclude
        )
        egy_postponed_dict = model_to_dict(
            education_group_year_postponed,
            exclude=fields_to_exclude
        )
        self.assertDictEqual(egy_dict, egy_postponed_dict)

        # Check if m2m is the same
        self.assertEqual(
            self.education_group_year.secondary_domains.all().count(),
            education_group_year_postponed.secondary_domains.all().count()
        )
        self.assertEqual(
            self.education_group_year.languages.all().count(),
            education_group_year_postponed.languages.all().count()
        )


class TestComputeEndPostponement(EducationGroupPostponementContextMixin):
    def test_education_group_max_postpone_years(self):
        expected_max_postpone = 6
        self.assertEqual(EDUCATION_GROUP_MAX_POSTPONE_YEARS, expected_max_postpone)

    def test_compute_end_postponement_case_no_specific_end_date_and_no_data_in_future(self):
        # Set end date of education group to None
        self.education_group_year.education_group.end_year = None
        self.education_group_year.refresh_from_db()
        # Remove all data in future
        EducationGroupYear.objects.filter(academic_year__year__gt=self.current_academic_year.year).delete()

        expected_end_year = self.current_academic_year.year + EDUCATION_GROUP_MAX_POSTPONE_YEARS
        result = _compute_end_year(self.education_group_year.education_group)
        self.assertEqual(result, expected_end_year)

    def test_compute_end_postponement_case_specific_end_date_and_no_data_in_future(self):
        # Set end date of education group
        self.education_group_year.education_group.end_year = self.current_academic_year.year + 2
        self.education_group_year.refresh_from_db()
        # Remove all data in future
        EducationGroupYear.objects.filter(academic_year__year__gt=self.current_academic_year.year).delete()

        result = _compute_end_year(self.education_group_year.education_group)
        self.assertEqual(result, self.education_group_year.education_group.end_year)

    def test_compute_end_postponement_case_specific_end_date_and_data_in_future_gte(self):
        # Set end date of education group
        self.education_group_year.education_group.end_year = self.current_academic_year.year + 2
        self.education_group_year.refresh_from_db()

        # Create data in future
        lastest_academic_year = self.generated_ac_years.academic_years[-1]
        field_to_exclude = ['id', 'external_id', 'academic_year', 'languages', 'secondary_domains']
        defaults = _model_to_dict(self.education_group_year, exclude=field_to_exclude)
        EducationGroupYear.objects.update_or_create(
            education_group=self.education_group_year.education_group,
            academic_year=lastest_academic_year,
            defaults=defaults
        )

        result = _compute_end_year(self.education_group_year.education_group)
        self.assertEqual(result, lastest_academic_year.year)


class TestPostponeEducationGroupYear(EducationGroupPostponementContextMixin):
    def test_postpone_education_group_case_new_in_future(self):
        ac_year_to_create = self.generated_ac_years.academic_years[0]
        egy_postponed = _postpone_education_group_year(
            self.education_group_year,
            ac_year_to_create,
        )

        self.assertIsInstance(egy_postponed, EducationGroupYear)
        self.assertEqual(egy_postponed.academic_year, ac_year_to_create)
        self.assertPostponementEquals(self.education_group_year, egy_postponed)

    def test_postpone_education_group_case_overide_existing_in_future(self):
        ac_year_in_future = self.generated_ac_years.academic_years[0]
        egy_future = EducationGroupYearFactory(
            education_group=self.education_group_year.education_group,
            academic_year=ac_year_in_future,
            weighting=True,
            default_learning_unit_enrollment=True
        )
        # Create one secondary domain
        egy_domain = EducationGroupYearDomainFactory(education_group_year=egy_future)

        # It will overide data of egy_future and keep data of self.educationgroupyear
        egy_postponed = _postpone_education_group_year(
            self.education_group_year,
            ac_year_in_future,
        )
        self.assertIsInstance(egy_postponed, EducationGroupYear)
        self.assertEqual(egy_postponed.academic_year, ac_year_in_future)
        self.assertPostponementEquals(self.education_group_year, egy_postponed)

        # Check that egy_domain is deleted
        with self.assertRaises(EducationGroupYearDomain.DoesNotExist):
            EducationGroupYearDomain.objects.get(id=egy_domain.id)


class TestStartPostponementEducationGroupYear(EducationGroupPostponementContextMixin):
    def test_start_postponement_case_multiple_creation(self):
        # Set end date of education group to None
        self.education_group_year.education_group.end_year = None
        self.education_group_year.refresh_from_db()

        start_year = self.education_group_year.academic_year.year
        egy_postponed_list = start(self.education_group_year.education_group, start_year=start_year)
        self.assertIsInstance(egy_postponed_list, list)
        self.assertEqual(len(egy_postponed_list), 6)

        for egy_postponed in egy_postponed_list:
            self.assertPostponementEquals(self.education_group_year, egy_postponed)


class TestGetStartEducationGroupYearPostponement(EducationGroupPostponementContextMixin):
    def test_get_start_education_group_year_case_found_data(self):
        result = _get_start_education_group_year(
            education_group=self.education_group_year.education_group,
            start_year=self.education_group_year.academic_year.year
        )
        self.assertEqual(result, self.education_group_year)

    def test_get_start_education_group_year_case_not_found_return_none(self):
        education_group = EducationGroupFactory()
        result = _get_start_education_group_year(
            education_group=education_group,
            start_year=2000
        )
        self.assertIsNone(result)
