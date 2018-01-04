import datetime
import os
import random
import time
import unittest
import pdb

import functools
import pyvirtualdisplay
import faker
import magic
import parse
import pendulum
from django.contrib.auth.models import Group, Permission
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils import timezone
from openpyxl import load_workbook
from prettyprinter import cpprint
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from base.models import session_exam_calendar
from base.tests.factories.academic_calendar import (AcademicCalendarExamSubmissionFactory,
                                                    AcademicCalendarFactory)
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.exam_enrollment import ExamEnrollmentFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_enrollment import \
    LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.offer_year_calendar import OfferYearCalendarFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.session_exam_calendar import \
    SessionExamCalendarFactory
from base.tests.factories.session_examen import SessionExamFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.user import SuperUserFactory, UserFactory

SIZE = (1280, 1280)

class BusinessMixin:
    def create_user(self):
        return UserFactory()

    def create_super_user(self):
        return SuperUserFactory()

    def add_group(self, user, *group_names):
        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            group.user_set.add(user)

    def add_permission(self, user, *permission_names):
        for permission_name in permission_names:
            if '.' in permission_name:
                label, codename = permission_name.split('.')
                permission = Permission.objects.get(codename=codename, content_type__app_label=label)
            else:
                permission = Permission.objects.get(codename=permission_name)

            user.user_permissions.add(permission)


class SeleniumTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.display = pyvirtualdisplay.Display(visible=0, size=SIZE)
        # self.display.start()
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {
            'download.default_directory': '/tmp',
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        })
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_window_size(*SIZE)

    def tearDown(self):
        self.driver.quit()
        # self.display.stop()

    def get_url_by_name(self, url_name, *args, **kwargs):
        url = '{}{}'.format(self.live_server_url, reverse(url_name, args=args, kwargs=kwargs))
        return url

    def goto(self, url_name, *args, **kwargs):
        url = self.get_url_by_name(url_name, *args, **kwargs)
        self.driver.get(url)

    def fill_by_id(self, field_id, value):
        field = self.driver.find_element_by_id(field_id)
        field.clear()
        field.send_keys(value)

    def login(self, username, password='password123'):
        self.goto('login')
        self.fill_by_id('id_username', username)
        self.fill_by_id('id_password', password)
        self.click_on('post_login_btn')

    def click_on(self, id_):
        self.driver.find_element_by_id(id_).click()

    def get_element(self, id_):
        return self.driver.find_element_by_id(id_)

    def get_element_text(self, id_):
        return self.get_element(id_).text

    def assertElementTextEqual(self, id_, text):
        self.assertEqual(self.get_element_text(id_), text)

    def assertCurrentUrl(self, url_name, *args, **kwargs):
        self.assertEqual(
            self.driver.current_url,
            self.get_url_by_name(url_name, *args, **kwargs)
        )


class Scenario1FunctionalTest(SeleniumTestCase, BusinessMixin):
    def setUp(self):
        super().setUp()
        self.user = self.create_super_user()
        # FIXME: Le super user n'a pas besoin de permission, est-ce que c'est un probleme ?
        # self.add_permission(self.user, 'can_access_academic_calendar')

        academic_year = AcademicYearFactory()
        self.academic_calendar = AcademicCalendarFactory.build(academic_year=academic_year)
        self.academic_calendar.save(functions=[])

    def test_01_scenario_modifier_periode_encoding(self):
        self.login(self.user.username)

        self.goto('academic_calendar_read', academic_calendar_id=self.academic_calendar.id)
        self.click_on('bt_academic_calendar_edit')

        new_date = self.academic_calendar.start_date - datetime.timedelta(days=5)
        new_date_str = new_date.strftime('%m/%d/%Y')

        self.fill_by_id('txt_start_date', new_date_str)

        self.driver.execute_script("scroll(0, 250)")
        self.click_on('bt_academic_calendar_save')

        self.assertCurrentUrl('academic_calendar_form',academic_calendar_id=self.academic_calendar.id)

        self.assertElementTextEqual('ac_start_date', new_date_str)

    def test_01_scenario_modifier_period_encoding_date_fin(self):
        self.login(self.user.username)

        self.goto('academic_calendar_read', academic_calendar_id=self.academic_calendar.id)
        self.click_on('bt_academic_calendar_edit')

        new_date = self.academic_calendar.end_date + datetime.timedelta(days=5)
        new_date_str = new_date.strftime('%m/%d/%Y')
        self.fill_by_id('txt_end_date', new_date_str)

        self.driver.execute_script("scroll(0, 250)")
        self.click_on('bt_academic_calendar_save')

        self.assertCurrentUrl('academic_calendar_form', academic_calendar_id=self.academic_calendar.id)

        self.assertElementTextEqual('ac_end_date', new_date_str)


class Scenario3FunctionalTest(SeleniumTestCase, BusinessMixin):
    def test(self):
        user = self.create_user()
        self.add_group(user, 'program_managers')
        self.add_permission(user, 'assessments.can_access_scoreencoding')

        start_date = timezone.now() + datetime.timedelta(days=20)

        academic_year = AcademicYearFactory(year=pendulum.today().year-1)

        academic_calendar = AcademicCalendarExamSubmissionFactory.build(
            academic_year=academic_year,
            start_date=start_date,
            end_date=start_date + datetime.timedelta(days=10),
        )
        academic_calendar.save(functions=[])

        person = PersonFactory(user=user)
        offer_year = OfferYearFactory(academic_year=academic_year)

        ProgramManagerFactory(offer_year=offer_year, person=person)

        sec = SessionExamCalendarFactory(academic_calendar=academic_calendar)

        self.login(user.username)

        self.goto('scores_encoding')

        warning_messages = self.driver.find_element_by_id('pnl_warning_messages')

        result = parse.parse(
            "La période d'encodage des notes pour la session {session:d} sera ouverte à partir du {date}",
            warning_messages.text
        )

        self.assertIsNotNone(result)
        # self.assertEqual(result['session'], 1)
        self.assertEqual(result['date'], academic_calendar.start_date.strftime('%d/%m/%Y'))


class Scenario4FunctionalTest(SeleniumTestCase, BusinessMixin):
    def test(self):
        user = self.create_user()
        self.add_group(user, 'program_managers')
        self.add_permission(user, 'can_access_academic_calendar', 'assessments.can_access_scoreencoding')

        academic_year = AcademicYearFactory(year=pendulum.today().year-1)
        academic_calendar = AcademicCalendarExamSubmissionFactory.build(academic_year=academic_year)
        academic_calendar.save(functions=[])

        person = PersonFactory(user=user)
        offer_year_factory = functools.partial(OfferYearFactory, academic_year=academic_year)

        acronyms = ['PHYS11BA', 'ECON2M1', 'PHYS1BA', 'PHYS2M1', 'PHYS2MA']
        offers = {
            acronym: offer_year_factory(acronym=acronym)
            for acronym in acronyms
        }

        program_manager_factory = functools.partial(
            ProgramManagerFactory, person=person
        )

        for acronym, offer_year in offers.items():
            program_manager_factory(offer_year=offer_year)

        student1 = StudentFactory()
        student2 = StudentFactory()
        student3 = StudentFactory()

        student10 = StudentFactory()
        student11 = StudentFactory()
        student12 = StudentFactory()
        student13 = StudentFactory()
        student14 = StudentFactory()
        student15 = StudentFactory()
        student16 = StudentFactory()

        offer_enrollment1 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student1)
        offer_enrollment2 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student2)
        offer_enrollment3 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student3)

        offer_enrollment10 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student10)
        offer_enrollment11 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student11)
        offer_enrollment12 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student12)
        offer_enrollment13 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student13)
        offer_enrollment14 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student14)
        offer_enrollment15 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student15)
        offer_enrollment16 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student16)

        offer_enrollment4 = OfferEnrollmentFactory(offer_year=offers['ECON2M1'], student=student1)
        offer_enrollment5 = OfferEnrollmentFactory(offer_year=offers['ECON2M1'], student=student2)

        # unité d'enseignement = learning_unit_year
        learning_unit = LearningUnitFactory()
        learning_unit_year_1 = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit)

        learning_unit2 = LearningUnitFactory()
        learning_unit_year_2 = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit2)

        learning_unit3 = LearningUnitFactory()
        learning_unit_year_3 = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit3)

        learning_unit_enrollment1 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment1, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment2 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment2, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment3 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment3, learning_unit_year=learning_unit_year_1)

        learning_unit_enrollment10 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment10, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment11 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment11, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment12 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment12, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment13 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment13, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment14 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment14, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment15 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment15, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment16 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment16, learning_unit_year=learning_unit_year_1)

        learning_unit_enrollment4 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment4, learning_unit_year=learning_unit_year_2)
        learning_unit_enrollment5 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment5, learning_unit_year=learning_unit_year_2)

        learning_unit_enrollment6 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment1, learning_unit_year=learning_unit_year_3)
        learning_unit_enrollment7 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment5, learning_unit_year=learning_unit_year_3)

        number_session = 1
        session_exam_phys11ba = SessionExamFactory(learning_unit_year=learning_unit_year_1, number_session=number_session, offer_year=offers['PHYS11BA'])

        session_exam_econ2m1 = SessionExamFactory(learning_unit_year=learning_unit_year_2, number_session=number_session, offer_year=offers['ECON2M1'])

        session_exam_3 = SessionExamFactory(learning_unit_year=learning_unit_year_3, number_session=number_session, offer_year=offers['ECON2M1'])
        session_exam_4 = SessionExamFactory(learning_unit_year=learning_unit_year_3, number_session=number_session, offer_year=offers['PHYS11BA'])

        offer_year_calendar = OfferYearCalendarFactory(academic_calendar=academic_calendar, offer_year=offers['PHYS11BA'])
        offer_year_calendar = OfferYearCalendarFactory(academic_calendar=academic_calendar, offer_year=offers['ECON2M1'])

        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment1, session_exam=session_exam_phys11ba)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment2, session_exam=session_exam_phys11ba)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment3, session_exam=session_exam_phys11ba)

        exam_enrollment_10 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment10, session_exam=session_exam_phys11ba)
        exam_enrollment_11 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment11, session_exam=session_exam_phys11ba)
        exam_enrollment_12 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment12, session_exam=session_exam_phys11ba)
        exam_enrollment_13 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment13, session_exam=session_exam_phys11ba)
        exam_enrollment_14 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment14, session_exam=session_exam_phys11ba)
        exam_enrollment_15 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment15, session_exam=session_exam_phys11ba)
        exam_enrollment_16 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment16, session_exam=session_exam_phys11ba)


        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment4, session_exam=session_exam_econ2m1)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment5, session_exam=session_exam_econ2m1)

        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment6, session_exam=session_exam_3)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment7, session_exam=session_exam_4)

        session_exam_calendar = SessionExamCalendarFactory(academic_calendar=academic_calendar)

        self.login(user.username)

        self.goto('scores_encoding')

        select = Select(self.driver.find_element_by_id('slt_offer_list_selection'))

        all_options = set(option.text for option in select.options)

        all_offers = set(offers.keys())

        self.assertSetEqual({'Tout'}, all_options - all_offers)

        item = self.driver.find_element_by_id('scores_encoding_learning_units')
        self.assertEqual(int(item.text), 3)
        self.assertEqual(len(all_options - {'Tout'}), 5)

        self.click_on('lnk_encode_{}'.format(learning_unit_year_1.id))

        # progression = self.driver.find_element_by_id('luy_progression').text
        # self.assertEqual(progression, '0 / 10')

        self.assertFalse(learning_unit_year_1.decimal_scores)
        self.assertEqual(
            self.driver.find_element_by_id('message_decimal_accepted').text,
             "Les notes de ce cours ne peuvent PAS recevoir de valeurs décimales."
        )

        self.assertEqual(
            int(self.driver.find_element_by_id('number_of_enrollments').text),
            10
        )

        the_first = 1
        element = self.driver.find_element_by_css_selector("[tabindex='%d']" % the_first)
        element_id = element.get_attribute('id')

        element.clear()
        element.send_keys(12)

        enrollment_id = int(element_id.split('_')[-1])

        self.click_on('bt_save_online_encoding_up')
        progression = self.driver.find_element_by_id('luy_progression').text
        self.assertEqual(progression, '1 / 10')

        self.assertEqual(
            int(self.driver.find_element_by_id('enrollment_note_{}'.format(enrollment_id)).text),
            12
        )

        element = self.driver.find_element_by_css_selector('td#enrollment_status_{} span'.format(enrollment_id))
        self.assertIn('glyphicon-send', element.get_attribute('class').split())

        self.click_on('lnk_encode')

        note_enrollments = {}

        for counter in range(2, 11):
            element = self.driver.find_element_by_css_selector("[tabindex='%d']" % counter)
            element_id = element.get_attribute('id')
            enrollment_id = int(element_id.split('_')[-1])
            self.fill_by_id(element_id, counter)
            note_enrollments[enrollment_id] = counter

        self.click_on('bt_save_online_encoding_up')

        progression = self.driver.find_element_by_id('luy_progression').text
        self.assertEqual(progression, '10 / 10')

        for enrollment_id, value in note_enrollments.items():
            self.assertEqual(
                int(self.driver.find_element_by_id('enrollment_note_{}'.format(enrollment_id)).text),
                value
            )

        self.click_on('lnk_encode')
        note_enrollments = set()

        for counter in range(1, 11):
            element = self.driver.find_element_by_css_selector("[tabindex='%d']" % counter)
            element_id = element.get_attribute('id')
            enrollment_id = int(element_id.split('_')[-1])
            element.clear()
            note_enrollments.add(enrollment_id)

        self.click_on('bt_save_online_encoding_up')

        progression = self.driver.find_element_by_id('luy_progression').text
        self.assertEqual(progression, '0 / 10')

        for enrollment_id in note_enrollments:
            self.assertEqual(
                self.driver.find_element_by_id('enrollment_note_{}'.format(enrollment_id)).text,
                '-'
            )

        progression = self.driver.find_element_by_id('luy_progression').text
        self.assertEqual(progression, '0 / 10')


class Scenario5FunctionalTest(SeleniumTestCase, BusinessMixin):
    def test(self):
        user = self.create_user()
        self.add_group(user, 'program_managers')
        self.add_permission(user, 'can_access_academic_calendar', 'assessments.can_access_scoreencoding')

        academic_year = AcademicYearFactory(year=pendulum.today().year-1)
        academic_calendar = AcademicCalendarExamSubmissionFactory.build(academic_year=academic_year)
        academic_calendar.save(functions=[])

        person = PersonFactory(user=user)
        offer_year_factory = functools.partial(OfferYearFactory, academic_year=academic_year)

        acronyms = ['PHYS11BA', 'ECON2M1', 'PHYS1BA', 'PHYS2M1', 'PHYS2MA']
        offers = {
            acronym: offer_year_factory(acronym=acronym)
            for acronym in acronyms
        }

        program_manager_factory = functools.partial(
            ProgramManagerFactory, person=person
        )

        for acronym, offer_year in offers.items():
            program_manager_factory(offer_year=offer_year)

        student1 = StudentFactory()
        student2 = StudentFactory()
        student3 = StudentFactory()

        student10 = StudentFactory()
        student11 = StudentFactory()
        student12 = StudentFactory()
        student13 = StudentFactory()
        student14 = StudentFactory()
        student15 = StudentFactory()
        student16 = StudentFactory()

        offer_enrollment1 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student1)
        offer_enrollment2 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student2)
        offer_enrollment3 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student3)

        offer_enrollment10 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student10)
        offer_enrollment11 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student11)
        offer_enrollment12 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student12)
        offer_enrollment13 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student13)
        offer_enrollment14 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student14)
        offer_enrollment15 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student15)
        offer_enrollment16 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student16)

        offer_enrollment4 = OfferEnrollmentFactory(offer_year=offers['ECON2M1'], student=student1)
        offer_enrollment5 = OfferEnrollmentFactory(offer_year=offers['ECON2M1'], student=student2)

        # unité d'enseignement = learning_unit_year
        learning_unit = LearningUnitFactory()
        learning_unit_year_1 = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit)

        learning_unit2 = LearningUnitFactory()
        learning_unit_year_2 = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit2)

        learning_unit3 = LearningUnitFactory()
        learning_unit_year_3 = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit3)

        learning_unit_enrollment1 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment1, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment2 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment2, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment3 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment3, learning_unit_year=learning_unit_year_1)

        learning_unit_enrollment10 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment10, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment11 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment11, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment12 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment12, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment13 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment13, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment14 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment14, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment15 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment15, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment16 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment16, learning_unit_year=learning_unit_year_1)

        learning_unit_enrollment4 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment4, learning_unit_year=learning_unit_year_2)
        learning_unit_enrollment5 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment5, learning_unit_year=learning_unit_year_2)

        learning_unit_enrollment6 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment1, learning_unit_year=learning_unit_year_3)
        learning_unit_enrollment7 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment5, learning_unit_year=learning_unit_year_3)

        number_session = 1
        session_exam_phys11ba = SessionExamFactory(learning_unit_year=learning_unit_year_1, number_session=number_session, offer_year=offers['PHYS11BA'])

        session_exam_econ2m1 = SessionExamFactory(learning_unit_year=learning_unit_year_2, number_session=number_session, offer_year=offers['ECON2M1'])

        session_exam_3 = SessionExamFactory(learning_unit_year=learning_unit_year_3, number_session=number_session, offer_year=offers['ECON2M1'])
        session_exam_4 = SessionExamFactory(learning_unit_year=learning_unit_year_3, number_session=number_session, offer_year=offers['PHYS11BA'])

        offer_year_calendar = OfferYearCalendarFactory(academic_calendar=academic_calendar, offer_year=offers['PHYS11BA'])
        offer_year_calendar = OfferYearCalendarFactory(academic_calendar=academic_calendar, offer_year=offers['ECON2M1'])

        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment1, session_exam=session_exam_phys11ba)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment2, session_exam=session_exam_phys11ba)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment3, session_exam=session_exam_phys11ba)

        exam_enrollment_10 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment10, session_exam=session_exam_phys11ba)
        exam_enrollment_11 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment11, session_exam=session_exam_phys11ba)
        exam_enrollment_12 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment12, session_exam=session_exam_phys11ba)
        exam_enrollment_13 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment13, session_exam=session_exam_phys11ba)
        exam_enrollment_14 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment14, session_exam=session_exam_phys11ba)
        exam_enrollment_15 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment15, session_exam=session_exam_phys11ba)
        exam_enrollment_16 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment16, session_exam=session_exam_phys11ba)


        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment4, session_exam=session_exam_econ2m1)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment5, session_exam=session_exam_econ2m1)

        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment6, session_exam=session_exam_3)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment7, session_exam=session_exam_4)

        session_exam_calendar = SessionExamCalendarFactory(academic_calendar=academic_calendar)

        self.login(user.username)

        self.goto('scores_encoding')

        select = Select(self.driver.find_element_by_id('slt_offer_list_selection'))
        # pdb.set_trace()
        select.select_by_visible_text('PHYS11BA')
        self.click_on('bt_submit_offer_search')
        time.sleep(1)
        self.click_on('lnk_via_excel')
        time.sleep(1)
        self.click_on('lnk_scores_encoding_download_{}'.format(learning_unit_year_1.id))
        time.sleep(1)
        filename = 'session_{}_{}_{}.xlsx'.format(academic_year.year, number_session, learning_unit_year_1.acronym)
        full_path = os.path.join('/', 'tmp', filename)

        print(full_path)
        self.assertTrue(os.path.exists(full_path))

        self.goto('online_encoding', learning_unit_year_id=learning_unit_year_1.id)
        self.click_on('bt_upload_score_modal')
        time.sleep(1)
        self.driver.execute_script("document.getElementById('fle_scores_input_file').style.display = 'block'")
        self.fill_by_id('fle_scores_input_file', full_path)
        time.sleep(1)
        self.click_on('bt_submit_upload_score_modal')
        # import pdb; pdb.set_trace()
        progression = self.driver.find_element_by_id('luy_progression').text
        self.assertEqual(progression, '0 / 10')


        # select.select_by_value('PHYS11BA')



@unittest.skip('WIP')
class Scenario5OldFunctionalTest(SeleniumTestCase, BusinessMixin):
    def update_xslx(self, filename, enrollments):
        fake = faker.Faker()

        wb = load_workbook(filename)

        sheet = wb.active

        if sheet.max_row > 11:
            start_row = 12
            for row_number, enrollment in enumerate(enrollments):  # range(12, sheet.max_row + 1):
                left_or_right = bool(random.getrandbits(1))
                selected_column = 'H' if left_or_right else 'I'

                if left_or_right:
                    value = random.randint(0, 20)
                    key = 'note'
                else:
                    value = fake.random_element(elements=('A', 'T', 'S', 'M'))
                    key = 'justification'

                sheet['{}{}'.format(selected_column, row_number + start_row)] = value
                enrollment[key] = value

        wb.save(filename=filename)

    def test_05_score_encoding(self):
        user = self.create_user() # create_super_user()
        group, created = Group.objects.get_or_create(name='program_managers')
        group.user_set.add(user)

        group, created = Group.objects.get_or_create(name='tutors')
        group.user_set.add(user)

        permission = Permission.objects.get(codename='can_access_academic_calendar')
        user.user_permissions.add(permission)
        permission = Permission.objects.filter(codename='can_access_scoreencoding', content_type__app_label='assessments').first()

        user.user_permissions.add(permission)

        self.login(user.username)

        academic_year = AcademicYearFactory(year=pendulum.today().year-1)
        academic_calendar = AcademicCalendarExamSubmissionFactory.build(academic_year=academic_year)
        academic_calendar.save(functions=[])
        # cpprint({k: getattr(academic_calendar, k) for k in ('start_date', 'end_date', 'reference')})

        person = PersonFactory(user=user)
        offer_year_phys11ba = OfferYearFactory(academic_year=academic_year, acronym='PHYS11BA')
        offer_year_econ2m1 = OfferYearFactory(academic_year=academic_year, acronym='ECON2M1')
        offer_year_phys1ba = OfferYearFactory(academic_year=academic_year, acronym='PHYS1BA')
        offer_year_phys2m1 = OfferYearFactory(academic_year=academic_year, acronym='PHYS2M1')
        offer_year_phys2ma = OfferYearFactory(academic_year=academic_year, acronym='PHYS2MA')

        ProgramManagerFactory(offer_year=offer_year_phys11ba, person=person)
        ProgramManagerFactory(offer_year=offer_year_econ2m1, person=person)
        ProgramManagerFactory(offer_year=offer_year_phys1ba, person=person)
        ProgramManagerFactory(offer_year=offer_year_phys2m1, person=person)
        ProgramManagerFactory(offer_year=offer_year_phys2ma, person=person)

        student1 = StudentFactory()
        student2 = StudentFactory()
        student3 = StudentFactory()
        student4 = StudentFactory()
        student5 = StudentFactory()

        learning_unit = LearningUnitFactory()
        learning_unit_year = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit)

        offer_enrollment1 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student1)
        offer_enrollment2 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student2)
        offer_enrollment3 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student3)
        offer_enrollment4 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student4)
        offer_enrollment5 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student5)

        learning_unit_enrollment1 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment1, learning_unit_year=learning_unit_year)
        learning_unit_enrollment2 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment2, learning_unit_year=learning_unit_year)
        learning_unit_enrollment3 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment3, learning_unit_year=learning_unit_year)
        learning_unit_enrollment4 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment4, learning_unit_year=learning_unit_year)
        learning_unit_enrollment5 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment5, learning_unit_year=learning_unit_year)

        number_session = 1
        session_exam = SessionExamFactory(learning_unit_year=learning_unit_year, number_session=number_session, offer_year=offer_year_phys11ba)
        offer_year_calendar = OfferYearCalendarFactory(academic_calendar=academic_calendar, offer_year=offer_year_phys11ba)

        enrollments = []
        for counter in range(1, 6):
            enrollments.append({
                'enrollment': ExamEnrollmentFactory(
                    learning_unit_enrollment=locals()['learning_unit_enrollment{}'.format(counter)],
                    session_exam=session_exam
                ),
                'note': None,
                'justification': None
            })

        sec = SessionExamCalendarFactory(academic_calendar=academic_calendar)

        diff_date = academic_calendar.end_date - academic_calendar.start_date

        days = diff_date.days / 2
        date = academic_calendar.start_date + datetime.timedelta(days=days)
        # cpprint({'diff_date': diff_date, 'days': days, 'date': date})

        self.assertIsNotNone(session_exam_calendar.current_session_exam(date))

        # Il faut une periode ouverte, sinon, on est retourne vers
        # assessments.views.score_encoding.outside_period

        self.goto('scores_encoding')
        # pdb.set_trace()
        self.driver.find_element_by_id('lnk_via_excel').click()
        time.sleep(1)
        self.driver.find_element_by_id('lnk_scores_encoding_download_{}'.format(learning_unit_year.id)).click()
        time.sleep(2)
        filename = 'session_{}_{}_{}.xlsx'.format(academic_year.year, number_session, learning_unit_year.acronym)
        full_path = os.path.join('/', 'tmp', filename)

        print(full_path)
        self.assertTrue(os.path.exists(full_path))

        self.update_xslx(full_path, enrollments)
        # pdb.set_trace()

        self.goto('online_encoding', learning_unit_year_id=learning_unit_year.id)
        self.driver.find_element_by_id('bt_upload_score_modal').click()
        time.sleep(1)
        self.driver.execute_script("document.getElementById('fle_scores_input_file').style.display = 'block'")
        self.fill_by_id('fle_scores_input_file', full_path)
        # time.sleep(1)
        self.driver.find_element_by_id('bt_submit_upload_score_modal').click()

        progression = self.driver.find_element_by_id('luy_progression').text
        self.assertEqual(progression, '0 / 5')

        for enrollment_idx, value in enumerate(enrollments):
            enrollment = value['enrollment']
            note = self.driver.find_element_by_id('enrollment_note_{}'.format(enrollment.id)).text
            if note != '-' and value['note'] is not None:
                self.assertEqual(value['note'], int(note))
            justification = self.driver.find_element_by_id('enrollment_justification_{}'.format(enrollment.id)).text
            if note != '-' and value['justification'] is not None:
                self.assertEqual(value['justification'], justification)

        # pdb.set_trace()
        # from openpyxl import load_workbook

        # Scenario 5, il y a un probleme, car je n'ai pas les memes registration_id dans les etudiants, et donc, l'algo ne les retrouve pas
        # ce qui fait que sans ce petit correctif, le test est erroné.


class Scenario6FunctionalTest(SeleniumTestCase, BusinessMixin):
    def test(self):
        user = self.create_user()
        self.add_group(user, 'program_managers')
        self.add_permission(user, 'can_access_academic_calendar', 'assessments.can_access_scoreencoding')

        academic_year = AcademicYearFactory(year=pendulum.today().year-1)
        academic_calendar = AcademicCalendarExamSubmissionFactory.build(academic_year=academic_year)
        academic_calendar.save(functions=[])

        person = PersonFactory(user=user)
        offer_year_factory = functools.partial(OfferYearFactory, academic_year=academic_year)

        acronyms = ['PHYS11BA', 'ECON2M1', 'PHYS1BA', 'PHYS2M1', 'PHYS2MA']
        offers = {
            acronym: offer_year_factory(acronym=acronym)
            for acronym in acronyms
        }

        program_manager_factory = functools.partial(
            ProgramManagerFactory, person=person
        )

        for acronym, offer_year in offers.items():
            program_manager_factory(offer_year=offer_year)

        student1 = StudentFactory()
        student2 = StudentFactory()
        student3 = StudentFactory()

        student10 = StudentFactory()
        student11 = StudentFactory()
        student12 = StudentFactory()
        student13 = StudentFactory()
        student14 = StudentFactory()
        student15 = StudentFactory()
        student16 = StudentFactory()

        offer_enrollment1 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student1)
        offer_enrollment2 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student2)
        offer_enrollment3 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student3)

        offer_enrollment10 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student10)
        offer_enrollment11 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student11)
        offer_enrollment12 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student12)
        offer_enrollment13 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student13)
        offer_enrollment14 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student14)
        offer_enrollment15 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student15)
        offer_enrollment16 = OfferEnrollmentFactory(offer_year=offers['PHYS11BA'], student=student16)

        offer_enrollment4 = OfferEnrollmentFactory(offer_year=offers['ECON2M1'], student=student1)
        offer_enrollment5 = OfferEnrollmentFactory(offer_year=offers['ECON2M1'], student=student2)

        # unité d'enseignement = learning_unit_year
        learning_unit = LearningUnitFactory()
        learning_unit_year_1 = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit)

        learning_unit2 = LearningUnitFactory()
        learning_unit_year_2 = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit2)

        learning_unit3 = LearningUnitFactory()
        learning_unit_year_3 = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit3)

        learning_unit_enrollment1 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment1, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment2 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment2, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment3 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment3, learning_unit_year=learning_unit_year_1)

        learning_unit_enrollment10 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment10, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment11 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment11, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment12 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment12, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment13 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment13, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment14 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment14, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment15 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment15, learning_unit_year=learning_unit_year_1)
        learning_unit_enrollment16 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment16, learning_unit_year=learning_unit_year_1)

        learning_unit_enrollment4 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment4, learning_unit_year=learning_unit_year_2)
        learning_unit_enrollment5 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment5, learning_unit_year=learning_unit_year_2)

        learning_unit_enrollment6 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment1, learning_unit_year=learning_unit_year_3)
        learning_unit_enrollment7 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment5, learning_unit_year=learning_unit_year_3)

        number_session = 1
        session_exam_phys11ba = SessionExamFactory(learning_unit_year=learning_unit_year_1, number_session=number_session, offer_year=offers['PHYS11BA'])

        session_exam_econ2m1 = SessionExamFactory(learning_unit_year=learning_unit_year_2, number_session=number_session, offer_year=offers['ECON2M1'])

        session_exam_3 = SessionExamFactory(learning_unit_year=learning_unit_year_3, number_session=number_session, offer_year=offers['ECON2M1'])
        session_exam_4 = SessionExamFactory(learning_unit_year=learning_unit_year_3, number_session=number_session, offer_year=offers['PHYS11BA'])

        offer_year_calendar = OfferYearCalendarFactory(academic_calendar=academic_calendar, offer_year=offers['PHYS11BA'])
        offer_year_calendar = OfferYearCalendarFactory(academic_calendar=academic_calendar, offer_year=offers['ECON2M1'])

        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment1, session_exam=session_exam_phys11ba)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment2, session_exam=session_exam_phys11ba)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment3, session_exam=session_exam_phys11ba)

        exam_enrollment_10 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment10, session_exam=session_exam_phys11ba)
        exam_enrollment_11 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment11, session_exam=session_exam_phys11ba)
        exam_enrollment_12 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment12, session_exam=session_exam_phys11ba)
        exam_enrollment_13 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment13, session_exam=session_exam_phys11ba)
        exam_enrollment_14 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment14, session_exam=session_exam_phys11ba)
        exam_enrollment_15 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment15, session_exam=session_exam_phys11ba)
        exam_enrollment_16 = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment16, session_exam=session_exam_phys11ba)


        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment4, session_exam=session_exam_econ2m1)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment5, session_exam=session_exam_econ2m1)

        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment6, session_exam=session_exam_3)
        ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment7, session_exam=session_exam_4)

        session_exam_calendar = SessionExamCalendarFactory(academic_calendar=academic_calendar)

        self.login(user.username)

        self.goto('scores_encoding')

        self.assertEqual(int(self.driver.find_element_by_id('scores_encoding_learning_units').text), 3)
        self.assertEqual(int(self.driver.find_element_by_id('scores_encoding_programs').text), 5)

        select = Select(self.driver.find_element_by_id('slt_offer_list_selection'))

        all_options = set(option.text for option in select.options)

        all_offers = set(offers.keys())

        self.assertSetEqual({'Tout'}, all_options - all_offers)

        item = self.driver.find_element_by_id('scores_encoding_learning_units')
        self.assertEqual(int(item.text), 3)
        self.assertEqual(len(all_options - {'Tout'}), 5)

        self.click_on('lnk_encode_{}'.format(learning_unit_year_1.id))
        self.assertEqual(
            int(self.driver.find_element_by_id('number_of_enrollments').text),
            10
        )

        note_enrollments = {}

        for counter in range(1, 11):
            element = self.driver.find_element_by_css_selector("[tabindex='%d']" % counter)
            element_id = element.get_attribute('id')
            enrollment_id = int(element_id.split('_')[-1])
            self.fill_by_id(element_id, counter)
            note_enrollments[enrollment_id] = counter

        self.click_on('bt_save_online_encoding_up')

        progression = self.driver.find_element_by_id('luy_progression').text
        self.assertEqual(progression, '10 / 10')

        for enrollment_id, value in note_enrollments.items():
            self.assertEqual(
                int(self.driver.find_element_by_id('enrollment_note_{}'.format(enrollment_id)).text),
                value
            )

        self.click_on('lnk_online_double_encoding')

        for enrollment_id, value in note_enrollments.items():
            self.fill_by_id('num_double_score_{}'.format(enrollment_id), str(value + 2))

        self.click_on('bt_compare_down')

        self.driver.execute_script("scroll(0, document.body.scrollHeight)")

        for enrollment_id in note_enrollments:
            self.click_on('bt_take_reencoded_{}'.format(enrollment_id))

        self.click_on('bt_submit_online_double_encoding_validation')

        self.driver.execute_script("scroll(0, document.body.scrollHeight)")

        for enrollment_id, value in note_enrollments.items():
            self.assertEqual(
                int(self.driver.find_element_by_id('enrollment_note_{}'.format(enrollment_id)).text),
                value + 2
            )


class Scenario7FunctionalTest(SeleniumTestCase, BusinessMixin):
    def test(self):
        user = self.create_user() # create_super_user()
        self.add_group(user, 'program_managers', 'tutors')
        self.add_permission(user, 'can_access_academic_calendar', 'assessments.can_access_scoreencoding')

        academic_year = AcademicYearFactory(year=pendulum.today().year-1)
        academic_calendar = AcademicCalendarExamSubmissionFactory.build(academic_year=academic_year)
        academic_calendar.save(functions=[])
        # cpprint({k: getattr(academic_calendar, k) for k in ('start_date', 'end_date', 'reference')})

        person = PersonFactory(user=user)
        offer_year_phys11ba = OfferYearFactory(academic_year=academic_year, acronym='PHYS11BA')
        offer_year_econ2m1 = OfferYearFactory(academic_year=academic_year, acronym='ECON2M1')
        offer_year_phys1ba = OfferYearFactory(academic_year=academic_year, acronym='PHYS1BA')
        offer_year_phys2m1 = OfferYearFactory(academic_year=academic_year, acronym='PHYS2M1')
        offer_year_phys2ma = OfferYearFactory(academic_year=academic_year, acronym='PHYS2MA')

        ProgramManagerFactory(offer_year=offer_year_phys11ba, person=person)
        ProgramManagerFactory(offer_year=offer_year_econ2m1, person=person)
        ProgramManagerFactory(offer_year=offer_year_phys1ba, person=person)
        ProgramManagerFactory(offer_year=offer_year_phys2m1, person=person)
        ProgramManagerFactory(offer_year=offer_year_phys2ma, person=person)

        student1 = StudentFactory()
        student2 = StudentFactory()
        student3 = StudentFactory()
        student4 = StudentFactory()
        student5 = StudentFactory()

        learning_unit = LearningUnitFactory()
        learning_unit_year = LearningUnitYearFactory(academic_year=academic_year, learning_unit=learning_unit)

        offer_enrollment1 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student1)
        offer_enrollment2 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student2)
        offer_enrollment3 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student3)
        offer_enrollment4 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student4)
        offer_enrollment5 = OfferEnrollmentFactory(offer_year=offer_year_phys11ba, student=student5)

        learning_unit_enrollment1 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment1, learning_unit_year=learning_unit_year)
        learning_unit_enrollment2 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment2, learning_unit_year=learning_unit_year)
        learning_unit_enrollment3 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment3, learning_unit_year=learning_unit_year)
        learning_unit_enrollment4 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment4, learning_unit_year=learning_unit_year)
        learning_unit_enrollment5 = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment5, learning_unit_year=learning_unit_year)

        number_session = 1

        session_exam = SessionExamFactory(learning_unit_year=learning_unit_year, number_session=number_session, offer_year=offer_year_phys11ba)
        offer_year_calendar = OfferYearCalendarFactory(academic_calendar=academic_calendar, offer_year=offer_year_phys11ba)

        enrollments = []
        for counter in range(1, 6):
            enrollments.append({
                'enrollment': ExamEnrollmentFactory(
                    learning_unit_enrollment=locals()['learning_unit_enrollment{}'.format(counter)],
                    session_exam=session_exam
                ),
                'note': None,
                'justification': None
            })

        sec = SessionExamCalendarFactory(academic_calendar=academic_calendar)

        self.login(user.username)

        self.goto('scores_encoding')
        self.fill_by_id('txt_acronym', learning_unit_year.acronym)
        self.click_on('bt_submit_offer_search')
        time.sleep(2)

        self.click_on('lnk_via_paper')
        # import pdb; pdb.set_trace()
        time.sleep(1)

        self.click_on('lnk_notes_printing_{}'.format(learning_unit_year.id))
        time.sleep(2)
        filename = 'Feuille de notes.pdf'
        full_path = os.path.join('/', 'tmp', filename)

        self.assertTrue(os.path.exists(full_path))

        mimetype = magic.from_file(full_path, mime=True)
        # import pdb; pdb.set_trace()
        self.assertEqual(mimetype, 'application/pdf')



