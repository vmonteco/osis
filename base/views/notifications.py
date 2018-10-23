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
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET

from base.utils import notifications
from base.views import layout
from osis_common.decorators.ajax import ajax_required


@login_required
@ajax_required
@require_POST
def clear_user_notifications(request):
    user = request.user
    notifications.clear_user_notifications(user)
    return layout.render(request, "blocks/notifications_inner.html", {})


@login_required
@ajax_required
@require_POST
def mark_notifications_as_read(request):
    user = request.user
    notifications.mark_notifications_as_read(user)
    return layout.render(request, "blocks/notifications_inner.html", {})
