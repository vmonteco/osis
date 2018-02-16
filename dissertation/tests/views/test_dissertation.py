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
from base.tests.factories.academic_year import AcademicYearFactory
from dissertation.tests.models.test_faculty_adviser import create_faculty_adviser
from dissertation.views.dissertation import adviser_can_manage
from django.test import TestCase
from django.core.urlresolvers import reverse
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.offer import OfferFactory
from base.tests.factories.student import StudentFactory
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.tests.factories.proposition_offer import PropositionOfferFactory
from osis_common.models import message_history


class DissertationViewTestCase(TestCase):
    fixtures = ['dissertation/fixtures/message_template.json', ]

    def setUp(self):
        self.manager = AdviserManagerFactory()
        a_person_teacher = PersonFactory.create(first_name='Pierre', last_name='Dupont')
        self.teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_student = PersonFactory.create(last_name="Durant", user=None)
        self.student = StudentFactory.create(person=a_person_student)
        self.offer1 = OfferFactory(title="test_offer1")
        self.offer2 = OfferFactory(title="test_offer2")
        self.academic_year1 = AcademicYearFactory()
        self.academic_year2 = AcademicYearFactory(year=self.academic_year1.year - 1)
        self.offer_year_start1 = OfferYearFactory(acronym="test_offer1", offer=self.offer1,
                                                  academic_year=self.academic_year1)
        self.offer_proposition1 = OfferPropositionFactory(offer=self.offer1, global_email_to_commission=True)
        self.offer_proposition2 = OfferPropositionFactory(offer=self.offer2, global_email_to_commission=False)
        self.proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                       creator=a_person_teacher,
                                                                       title='Proposition 1212121'
                                                                       )
        FacultyAdviserFactory(adviser=self.manager, offer=self.offer1)
        self.dissertation_test_email = DissertationFactory(author=self.student,
                                                           title='Dissertation_test_email',
                                                           offer_year_start=self.offer_year_start1,
                                                           proposition_dissertation=self.proposition_dissertation,
                                                           status='DRAFT',
                                                           active=True,
                                                           dissertation_role__adviser=self.teacher,
                                                           dissertation_role__status='PROMOTEUR'
                                                           )

        roles = ['PROMOTEUR', 'CO_PROMOTEUR', 'READER', 'PROMOTEUR', 'ACCOMPANIST', 'PRESIDENT']
        status = ['DRAFT', 'COM_SUBMIT', 'EVA_SUBMIT', 'TO_RECEIVE', 'DIR_SUBMIT', 'DIR_SUBMIT']

        for x in range(0, 6):
            proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                      creator=a_person_teacher,
                                                                      title='Proposition {}'.format(x)
                                                                      )
            PropositionOfferFactory(proposition_dissertation=proposition_dissertation,
                                    offer_proposition=self.offer_proposition1)

            DissertationFactory(author=self.student,
                                title='Dissertation {}'.format(x),
                                offer_year_start=self.offer_year_start1,
                                proposition_dissertation=proposition_dissertation,
                                status=status[x],
                                active=True,
                                dissertation_role__adviser=self.teacher,
                                dissertation_role__status=roles[x]
                                )

    def test_get_dissertations_list_for_teacher(self):
        self.client.force_login(self.teacher.person.user)
        url = reverse('dissertations_list')
        response = self.client.get(url)
        self.assertEqual(response.context[-1]['adviser_list_dissertations'].count(), 1)  # only 1 because 1st is DRAFT
        self.assertEqual(response.context[-1]['adviser_list_dissertations_copro'].count(), 1)
        self.assertEqual(response.context[-1]['adviser_list_dissertations_reader'].count(), 1)
        self.assertEqual(response.context[-1]['adviser_list_dissertations_accompanist'].count(), 1)
        self.assertEqual(response.context[-1]['adviser_list_dissertations_president'].count(), 1)

    def test_get_dissertations_list_for_manager(self):
        self.client.force_login(self.manager.person.user)
        url = reverse('manager_dissertations_list')
        response = self.client.get(url)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

    def test_search_dissertations_for_manager(self):
        self.client.force_login(self.manager.person.user)
        url = reverse('manager_dissertations_search')

        response = self.client.get(url, data={"search": "no result search"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 0)

        response = self.client.get(url, data={"search": "Dissertation 2"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 1)

        response = self.client.get(url, data={"search": "Proposition 3"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 1)

        response = self.client.get(url, data={"search": "Dissertation"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"search": "Dissertation",
                                              "offer_prop_search": self.offer_proposition1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"search": "Dissertation",
                                              "offer_prop_search": self.offer_proposition2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 0)

        response = self.client.get(url, data={"academic_year": self.academic_year1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"academic_year": self.academic_year2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 0)

        response = self.client.get(url, data={"status_search": "COM_SUBMIT"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 1)

        response = self.client.get(url, data={"search": "test_offer"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"search": "Durant"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

        response = self.client.get(url, data={"search": "Dupont"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[-1]['dissertations'].count(), 7)

    def test_adviser_can_manage_dissertation(self):
        manager = AdviserManagerFactory()
        manager2 = AdviserManagerFactory()
        a_person_teacher = PersonFactory.create(first_name='Pierre', last_name='Dupont')
        teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_student = PersonFactory.create(last_name="Durant", user=None)
        student = StudentFactory.create(person=a_person_student)
        offer_year_start = OfferYearFactory(academic_year=self.academic_year1, acronym="test_offer2")
        offer_year_start2 = OfferYearFactory(acronym="test_offer3", academic_year=offer_year_start.academic_year)
        offer = offer_year_start.offer
        offer2 = offer_year_start2.offer
        FacultyAdviserFactory(adviser=manager, offer=offer)
        create_faculty_adviser(manager, offer)
        create_faculty_adviser(manager2, offer2)
        proposition_dissertation = PropositionDissertationFactory(author=teacher,
                                                                  creator=a_person_teacher,
                                                                  title='Proposition1')
        dissertation = DissertationFactory(author=student,
                                           title='Dissertation 2017',
                                           offer_year_start=offer_year_start,
                                           proposition_dissertation=proposition_dissertation,
                                           status='DIR_SUBMIT',
                                           active=True,
                                           dissertation_role__adviser=teacher,
                                           dissertation_role__status='PROMOTEUR')
        self.assertEqual(adviser_can_manage(dissertation, manager), True)
        self.assertEqual(adviser_can_manage(dissertation, manager2), False)
        self.assertEqual(adviser_can_manage(dissertation, teacher), False)

    def test_email_dissert(self):
        count_messages_before_status_change = len(message_history.find_my_messages(self.teacher.person.id))
        self.dissertation_test_email.go_forward()
        message_history_result = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        assert 'Vous avez reçu une demande d\'encadrement de mémoire' in message_history_result.last().subject
        count_messages_before_status_change = len(
            message_history.find_my_messages(self.dissertation_test_email.author.person.id))
        self.dissertation_test_email.refuse()
        message_history_result = message_history.find_my_messages(self.dissertation_test_email.author.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        assert 'Votre projet de mémoire n\'a pas été validé par votre promoteur' in \
               message_history_result.last().subject
        count_messages_before_status_change = len(
            message_history.find_my_messages(self.dissertation_test_email.author.person.id))
        self.dissertation_test_email.go_forward()
        self.dissertation_test_email.manager_accept()
        message_history_result_after = message_history.find_my_messages(self.dissertation_test_email.author.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result_after))
        assert 'Votre projet de mémoire est validé par votre promoteur' in message_history_result_after.last().subject
        count_message_history_result_author = len(
            message_history.find_my_messages(self.dissertation_test_email.author.person.id))
        count_message_history_result_promoteur = len(message_history.find_my_messages(
            self.teacher.person.id))
        self.dissertation_test_email.refuse()
        message_history_result_author_after_change = message_history.find_my_messages(
            self.dissertation_test_email.author.person.id)
        message_history_result_promoteur_after_change = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_message_history_result_author + 1, len(message_history_result_author_after_change))
        self.assertEqual(count_message_history_result_promoteur + 1, len(message_history_result_promoteur_after_change))
        assert 'La commission Mémoires n\'a pas validé le projet de mémoire' in \
               message_history_result_promoteur_after_change.last().subject
        assert 'La commission Mémoires n\'a pas validé votre projet de mémoire' in \
               message_history_result_author_after_change.last().subject
        count_message_history_result_author = len(
            message_history.find_my_messages(self.dissertation_test_email.author.person.id))
        count_message_history_result_promoteur = len(message_history.find_my_messages(
            self.teacher.person.id))
        self.dissertation_test_email.manager_accept()
        self.offer_proposition1.global_email_to_commission = False
        message_history_result_author_after_change = message_history.find_my_messages(
            self.dissertation_test_email.author.person.id)
        message_history_result_promoteur_after_change = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_message_history_result_author + 1, len(message_history_result_author_after_change))
        self.assertEqual(count_message_history_result_promoteur + 1, len(message_history_result_promoteur_after_change))
        assert 'La commission Mémoires a accepté le projet de Mémoire :' in \
               message_history_result_promoteur_after_change.last().subject
        assert 'La commission Mémoires a accepté votre projet de mémoire' in \
               message_history_result_author_after_change.last().subject
