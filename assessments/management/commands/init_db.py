import random

import factory
import pendulum
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from attribution.tests.factories.attribution import AttributionFactory
from base.models.offer_year import OfferYear
from base.models.session_exam_calendar import SessionExamCalendar
from base.models.student import Student
from base.tests.factories.academic_calendar import AcademicCalendarExamSubmissionFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.exam_enrollment import ExamEnrollmentFactory
from base.tests.factories.learning_unit_enrollment import LearningUnitEnrollmentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.offer_year_calendar import OfferYearCalendarFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.program_manager import ProgramManagerFactory
from base.tests.factories.session_exam_calendar import SessionExamCalendarFactory
from base.tests.factories.session_examen import SessionExamFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory


class OfferEnrollmentRandomStudentFactory(OfferEnrollmentFactory):
    student = factory.Iterator(Student.objects.all())

class Command(BaseCommand):
    def create_learning_units_with_exams(self, tutor, academic_year, session_exam_calendar, offer_year):
        learning_unit_year = LearningUnitYearFactory(academic_year=academic_year)
        AttributionFactory(tutor=tutor, learning_unit_year=learning_unit_year, score_responsible=True)

        session_exam = SessionExamFactory(
            learning_unit_year=learning_unit_year,
            number_session=session_exam_calendar.number_session,
            offer_year=offer_year
        )

        for counter in range(random.randrange(5, 50)):
            # student = StudentFactory()
            offer_enrollment = OfferEnrollmentRandomStudentFactory(offer_year=offer_year) # , student=student)
            learning_unit_enrollment = LearningUnitEnrollmentFactory(offer_enrollment=offer_enrollment,
                                                                     learning_unit_year=learning_unit_year)
            exam_enrollment = ExamEnrollmentFactory(learning_unit_enrollment=learning_unit_enrollment,
                                                    session_exam=session_exam)

    def handle(self, *args, **options):
        user = UserFactory()
        self.stdout.write('user: {}'.format(user.username))

        person = PersonFactory(user=user, language='fr-be')

        group, created = Group.objects.get_or_create(name='program_managers')
        group.user_set.add(user)

        permission = Permission.objects.get(codename='can_access_academic_calendar')
        user.user_permissions.add(permission)

        permission = Permission.objects.get(codename='can_access_scoreencoding', content_type__app_label='assessments')
        user.user_permissions.add(permission)

        academic_year = AcademicYearFactory(year=pendulum.today().year - 1)
        academic_calendar = AcademicCalendarExamSubmissionFactory(academic_year=academic_year)

        acronyms = ['PHYS11BA', 'ECON2M1', 'PHYS1BA', 'PHYS2M1', 'PHYS2MA']

        offers = {
            acronym: OfferYearFactory(academic_year=academic_year, acronym=acronym)
            for acronym in acronyms
        }

        for offer in offers.values():
            ProgramManagerFactory(offer_year=offer, person=person)

        # offer_year = offers['PHYS11BA']

        tutor = TutorFactory(person=person)

        if SessionExamCalendar.objects.exists():
            session_exam_calendar = SessionExamCalendar.objects.first()
        else:
            session_exam_calendar = SessionExamCalendarFactory(academic_calendar=academic_calendar)


        for counter in range(200):
            student = StudentFactory()

        for offer_year in OfferYear.objects.all():
            offer_year_calendar = OfferYearCalendarFactory(academic_calendar=academic_calendar,
                                                           offer_year=offer_year)

            for counter in range(random.randint(5, 10)):
                self.create_learning_units_with_exams(tutor, academic_year, session_exam_calendar, offer_year)

        # transaction.rollback()
        