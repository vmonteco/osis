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
from django.core.cache import cache
from functools import wraps

CACHE_FILTER_TIMEOUT = None


def cache_filter(param_list=None):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            param_encoded = [{key: value} for key, value in request.GET.items() if key in param_list]  \
                            if param_list else request.GET
            _save_to_cache(request, param_encoded)
            return func(request, *args, **kwargs)
        return inner
    return decorator


def _save_to_cache(request, param_to_cache):
    key = get_filter_key(request)
    cache.set(key, param_to_cache, timeout=CACHE_FILTER_TIMEOUT)


def _get_from_cache(request):
    key = get_filter_key(request)
    return cache.get(key)


def get_filter_key(request):
    user = request.user
    path = request.path
    return "_".join([str(user.id), path])