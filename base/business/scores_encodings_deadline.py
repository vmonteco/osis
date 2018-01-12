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

from base.models.enums import academic_calendar_type as ac_type
from base.models.offer_year_calendar import OfferYearCalendar
from base.models.session_exam_calendar import SessionExamCalendar
from base.models.session_exam_deadline import SessionExamDeadline


def compute_deadline_by_offer_year_calendar(oyc):
    if _is_valid_offer_year_calendar(oyc):
        return

    oyc_deliberation = _get_oyc_deliberation(oyc)
    oyc_scores_exam_submission = _get_oyc_scores_exam_submission(oyc)

    end_date_offer_year = _one_day_before_end_date(oyc_deliberation)
    score_submission_date = _one_day_before_end_date(oyc_scores_exam_submission)

    end_date_academic = oyc_deliberation.academic_calendar.end_date if oyc_deliberation else None
    sessions_exam_deadlines = _get_list_sessions_exam_deadlines(oyc_deliberation)

    _save_new_deadlines(sessions_exam_deadlines, end_date_academic, end_date_offer_year, score_submission_date)


def _is_valid_offer_year_calendar(oyc):
    return oyc.academic_calendar.reference not in (ac_type.DELIBERATION, ac_type.SCORES_EXAM_SUBMISSION)


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
    session = getattr(oyc.academic_calendar, 'sessionexamcalendar', None)
    if not session:
        return None
    try:
        return OfferYearCalendar.objects.filter(
            education_group_year=oyc.education_group_year,
            academic_calendar__reference=reference,
            academic_calendar__sessionexamcalendar__number_session=session.number_session
        ).get()
    except OfferYearCalendar.DoesNotExist:
        return None


def _get_list_sessions_exam_deadlines(oyc_deliberation):
    if not oyc_deliberation:
        return []

    session = SessionExamCalendar.objects.get(academic_calendar=oyc_deliberation.academic_calendar)
    return SessionExamDeadline.objects.filter(
        offer_enrollment__offer_year=oyc_deliberation.offer_year, number_session=session.number_session)


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
