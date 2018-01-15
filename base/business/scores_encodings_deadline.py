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
import datetime
import logging
from django.conf import settings

from base.models import session_exam_calendar, offer_year_calendar
from base.models.enums import academic_calendar_type as ac_type
from base.models.offer_year_calendar import OfferYearCalendar
from base.models.session_exam_deadline import SessionExamDeadline


logger = logging.getLogger(settings.DEFAULT_LOGGER)


def compute_deadline(off_year_calendar):
    if not _impact_scores_encodings_deadlines(off_year_calendar):
        return

    oyc_deliberation = _get_oyc_deliberation(off_year_calendar)
    oyc_scores_exam_submission = _get_oyc_scores_exam_submission(off_year_calendar)

    end_date_offer_year = _one_day_before_end_date(oyc_deliberation)
    score_submission_date = oyc_scores_exam_submission.end_date.date() \
        if oyc_scores_exam_submission and oyc_scores_exam_submission.end_date else None

    end_date_academic = oyc_deliberation.academic_calendar.end_date if oyc_deliberation else None
    sessions_exam_deadlines = _get_list_sessions_exam_deadlines(off_year_calendar.academic_calendar,
                                                                off_year_calendar.offer_year)

    _save_new_deadlines(sessions_exam_deadlines, end_date_academic, end_date_offer_year, score_submission_date)


def _impact_scores_encodings_deadlines(oyc):
    return oyc.academic_calendar.reference in (ac_type.DELIBERATION, ac_type.SCORES_EXAM_SUBMISSION)


def _save_new_deadlines(sessions_exam_deadlines, end_date_academic, end_date_offer_year, score_submission_date):
    for session in sessions_exam_deadlines:
        end_date_student = _one_day_before(session.deliberation_date)

        new_deadline = min(filter(None, (end_date_academic, end_date_offer_year, end_date_student)))
        new_deadline_tutor = _compute_delta_deadline_tutor(new_deadline, score_submission_date)

        if _is_deadline_changed(session, new_deadline, new_deadline_tutor):
            session.deadline = new_deadline
            session.deadline_tutor = new_deadline_tutor
            session.save()


def _is_deadline_changed(session, new_deadline, new_deadline_tutor):
    return new_deadline != session.deadline or new_deadline_tutor != session.deadline_tutor


def _get_oyc_scores_exam_submission(oyc):
    if oyc.academic_calendar.reference == ac_type.DELIBERATION:
        oyc_scores_exam_submission = _get_oyc_by_reference(ac_type.SCORES_EXAM_SUBMISSION, oyc)
    else:
        oyc_scores_exam_submission = oyc
    return oyc_scores_exam_submission


def _get_oyc_deliberation(oyc):
    if oyc.academic_calendar.reference == ac_type.DELIBERATION:
        oyc_deliberation = oyc
    else:
        oyc_deliberation = _get_oyc_by_reference(ac_type.DELIBERATION, oyc)
    return oyc_deliberation


def _get_oyc_by_reference(reference, oyc):
    number_session = session_exam_calendar.get_number_session_by_academic_calendar(oyc.academic_calendar)
    if number_session:
        try:
            return offer_year_calendar.search(education_group_year_id=oyc.education_group_year,
                                              academic_calendar_reference=reference,
                                              number_session=number_session).get()
        except OfferYearCalendar.DoesNotExist:
            return None


def _get_list_sessions_exam_deadlines(academic_calendar, offer_year):
    session_exam_deadlines = []
    number_session = session_exam_calendar.get_number_session_by_academic_calendar(academic_calendar)
    if number_session:
        session_exam_deadlines = SessionExamDeadline.objects.filter(
            offer_enrollment__offer_year=offer_year, number_session=number_session)
    else:
        msg = "No SessionExamCalendar (number session) found for academic calendar = {}"
        logger.warning(msg.format(academic_calendar.title))
    return session_exam_deadlines


def _one_day_before_end_date(oyc):
    return _one_day_before(oyc.end_date.date()) if oyc and oyc.end_date else None


def _one_day_before(current_date):
    result = None
    if isinstance(current_date, datetime.date):
        result = current_date - datetime.timedelta(days=1)
    return result


def _compute_delta_deadline_tutor(deadline, score_submission_date):
    if deadline and score_submission_date and deadline >= score_submission_date:
        return (deadline - score_submission_date).days
