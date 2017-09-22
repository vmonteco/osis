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
from django.conf import settings

CONTEXT_KEY_PREVIOUS = 'previous_object'
CONTEXT_KEY_NEXT = 'next_object'


def set_objects_ids(request, session_key, list_ids):
    if settings.CACHE_ENABLED:
        request.session[session_key] = list_ids


def get_next_and_previous_object(request, session_key, current_id):
    object_ids = request.session.get(session_key, []) if settings.CACHE_ENABLED else []
    current_index_id = _get_current_index(object_ids, current_id)
    return {
        CONTEXT_KEY_PREVIOUS: _get_previous_id_object(object_ids, current_index_id),
        CONTEXT_KEY_NEXT:  _get_next_id_object(object_ids, current_index_id)
    }


def _get_current_index(list_ids, current_id):
    return next((i for i, item in enumerate(list_ids) if item.get('id') == int(current_id)), None)


def _get_next_id_object(list_ids, current_index_id):
    try:
        return list_ids[current_index_id + 1]
    except:
        return None


def _get_previous_id_object(list_ids, current_index_id):
    return list_ids[current_index_id - 1] if current_index_id > 0 else None
