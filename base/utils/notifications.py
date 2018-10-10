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
import itertools
import time

from base.utils.cache import cache

CACHE_NOTIFICATIONS_TIMEOUT = 1800  # seconds -> 30 min
NOTIFICATIONS_UNREAD_KEY = "notifications_unread_user_{}"
NOTIFICATIONS_READ_KEY = "notifications_read_user_{}"
NOTIFICATIONS_TIMESTAMP = "notifications_last_read_user_{}"

READ_STATE = "read"
UNREAD_STATE = "unread"


def get_user_notifications(user):
    return list(itertools.chain(get_user_unread_notifications(user),
                           get_user_read_notifications(user)))

def get_user_unread_notifications(user):
    return user.notifications.unread()


def get_user_read_notifications(user):
    return user.notifications.read()


def mark_notifications_as_read(user):
    user.notifications.mark_all_as_read()


def clear_user_notifications(user):
    user.notifications.mark_all_as_deleted()


def get_notifications_last_time_read_for_user(user):
    cache_key = make_notifications_timestamp_cache_key(user)
    timestamp_last_read = cache.get(cache_key)
    return datetime.datetime.fromtimestamp(float(timestamp_last_read)) if timestamp_last_read else None


def set_notifications_last_read_as_now_for_user(user):
    cache_key = make_notifications_timestamp_cache_key(user)
    cache.set(cache_key, str(time.time()))


def make_notifications_timestamp_cache_key(user):
    return NOTIFICATIONS_TIMESTAMP.format(user.pk)
