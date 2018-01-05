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

from django.db import transaction

from base.models import offer_year_calendar
from base.models.enums import academic_calendar_type
from base.models.session_exam_calendar import SessionExamCalendar
from base.models.session_exam_deadline import SessionExamDeadline


def compute_deadline_by_offer_year_calendar(oyc):
    if oyc.academic_calendar.reference not in (academic_calendar_type.DELIBERATION,
                                               academic_calendar_type.SCORES_EXAM_SUBMISSION):
        return

    education_group_year = oyc.education_group_year
    if oyc.academic_calendar.reference == academic_calendar_type.DELIBERATION:
        oyc_deliberation = oyc
        oyc_scores_exam_submission = offer_year_calendar.search(education_group_year_id=education_group_year,
                                                                academic_calendar_reference=academic_calendar_type.SCORES_EXAM_SUBMISSION)\
                                                        .first()
    else:
        oyc_deliberation = offer_year_calendar.search(education_group_year_id=education_group_year,
                                                      academic_calendar_reference=academic_calendar_type.DELIBERATION)\
                                              .first()
        oyc_scores_exam_submission = oyc

    end_date_offer_year = _one_day_before(oyc_deliberation.end_date.date()) if oyc_deliberation and oyc_deliberation.end_date else None
    end_date_academic = oyc_deliberation.academic_calendar.end_date
    score_submission_date = oyc_scores_exam_submission.end_date.date() if oyc_scores_exam_submission and oyc_scores_exam_submission.end_date else None

    list_sessions = SessionExamCalendar.objects.filter(academic_calendar=oyc_deliberation.academic_calendar).values('number_session')
    sessions_exam_deadlines = SessionExamDeadline.objects.filter(offer_enrollment__offer_year=oyc_deliberation.offer_year,
                                                                 number_session__in=list_sessions)

    with transaction.atomic():
        for session in sessions_exam_deadlines:
            deadline = session.deadline
            deadline_tutor = session.deadline_tutor

            end_date_student = _one_day_before(session.deliberation_date) if session.deliberation_date else None

            new_deadline = min(filter(None, (end_date_academic, end_date_offer_year, end_date_student)))
            new_deadline_tutor = _get_delta_deadline_tutor(new_deadline, score_submission_date)
            if new_deadline == deadline and deadline_tutor == new_deadline_tutor:
                continue

            session.deadline = new_deadline
            session.deadline_tutor = new_deadline_tutor
            session.save()


def _one_day_before(current_date):
    return current_date - datetime.timedelta(days=1)


def _get_delta_deadline_tutor(deadline, score_submission_date):
    if deadline and score_submission_date and deadline >= score_submission_date:
        return (deadline - score_submission_date).days
