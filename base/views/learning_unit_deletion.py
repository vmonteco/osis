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
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from base import models as mdl
from base.business import learning_unit_deletion
from base.utils.send_mail import send_mail_after_the_learning_unit_year_deletion
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from base.views import layout
from base.models import learning_unit_year as learning_unit_year_mdl


@login_required
@permission_required('base.can_delete_learningunit', raise_exception=True)
def delete_from_given_learning_unit_year(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.get_by_id(learning_unit_year_id)
    messages_deletion = learning_unit_deletion.check_learning_unit_year_deletion(learning_unit_year)
    if not messages_deletion and request.method == 'POST':
        try:
            result = learning_unit_deletion.delete_from_given_learning_unit_year(learning_unit_year)
            success_msg = _("You asked the deletion of the learning unit %(acronym)s from the year %(year)s") \
                          % {'acronym': learning_unit_year.acronym,
                             'year': learning_unit_year.academic_year}
            messages.add_message(request, messages.SUCCESS, success_msg)

            for msg in sorted(result):
                messages.add_message(request, messages.SUCCESS, msg)

            send_mail_after_the_learning_unit_year_deletion([], learning_unit_year.acronym,
                                                            learning_unit_year.academic_year, result)

        except ProtectedError as e:
            messages.add_message(request, messages.ERROR, str(e))

        return redirect('learning_units')

    else:
        if messages_deletion:
            context = {'title': _("cannot_delete_learning_unit_year")
                                % {'learning_unit': learning_unit_year.acronym,
                                   'year': learning_unit_year.academic_year},
                       'messages_deletion': sorted(messages_deletion.values())}
        else:
            learning_units_to_delete = learning_unit_year.find_gte_learning_units_year()

            context = {'title': _("msg_warning_delete_learning_unit") % learning_unit_year,
                       'learning_units_to_delete': learning_units_to_delete}

        return layout.render(request, "learning_unit/deletion.html", context)


@login_required
@permission_required('base.can_delete_learningunit', raise_exception=True)
def delete_all_learning_units_year(request, learning_unit_year_id):
    learning_unit_year = mdl.learning_unit_year.get_by_id(learning_unit_year_id)
    learning_unit = learning_unit_year.learning_unit

    messages_deletion = learning_unit_deletion.check_learning_unit_deletion(learning_unit)

    if not messages_deletion and request.method == 'POST':
        try:
            result = learning_unit_deletion.delete_learning_unit(learning_unit)
            messages.add_message(request, messages.SUCCESS,
                                 _("The learning unit %(acronym)s has been successfully deleted for all years.")
                                 % {'acronym': learning_unit.acronym})
            for message_deletion in sorted(result):
                messages.add_message(request, messages.SUCCESS, message_deletion)

            send_mail_after_the_learning_unit_year_deletion([], learning_unit.acronym, None, result)

        except ProtectedError as e:
            messages.add_message(request, messages.ERROR, str(e))

        return redirect('learning_units')

    else:
        if messages_deletion:
            context = {'title': _('cannot_delete_learning_unit') % {'learning_unit': learning_unit.acronym},
                       'messages_deletion': sorted(messages_deletion.values())}
        else:
            context = {'title': _('msg_warning_delete_learning_unit') % learning_unit,
                       'learning_units_to_delete': learning_unit_year_mdl.search(learning_unit=learning_unit)
                           .order_by('academic_year__year')}

        return layout.render(request, "learning_unit/deletion.html", context)
