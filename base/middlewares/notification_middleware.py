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
import datetime
import time

from notifications.signals import notify
from base.utils.cache import cache

from base.models import academic_calendar

ALERT_WEEK = 2

class NotificationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        send_academic_calendar_notifications(request.user)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


def send_academic_calendar_notifications(user):
    cache_key = make_cache_key(user)
    timestamp_last_read = cache.get(cache_key)


    ac_qs = academic_calendar.AcademicCalendar.objects.starting_within(weeks=ALERT_WEEK).\
        order_by("start_date", "end_date")

    if timestamp_last_read:
        date_obj = datetime.date.fromtimestamp(float(timestamp_last_read))
        ac_qs = ac_qs.filter(start_date__gt=date_obj+datetime.timedelta(weeks=ALERT_WEEK))

    for ac_obj in ac_qs:
        notify.send(ac_obj, recipient=user, verb=str(ac_obj))

    cache.set(cache_key, str(time.time()))


def make_cache_key(user):
    return "notifications_last_read_user_{}".format(user.pk)
