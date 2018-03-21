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
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.business import learning_unit_year_with_context
from base.business.learning_units.edition import ConsistencyError
from base.forms.learning_unit.edition import LearningUnitEndDateForm, LearningUnitModificationForm
from base.forms.learning_unit.edition_volume import VolumeEditionFormsetContainer
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.views import layout
from base.views.common import display_error_messages, display_success_messages
from base.views.learning_unit import get_learning_unit_identification_context, \
    get_common_context_learning_unit_year, learning_unit_components, _check_credits
from base.views.learning_units import perms


@login_required
@permission_required('base.can_edit_learningunit_date', raise_exception=True)
@perms.can_perform_end_date_modification
def learning_unit_edition_end_date(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    person = get_object_or_404(Person, user=request.user)

    context = get_learning_unit_identification_context(learning_unit_year_id, person)

    learning_unit_to_edit = learning_unit_year.learning_unit
    form = LearningUnitEndDateForm(request.POST or None, learning_unit=learning_unit_to_edit)
    if form.is_valid():
        try:
            result = form.save()
            display_success_messages(request, result)

            learning_unit_year_id = _get_current_learning_unit_year_id(learning_unit_to_edit, learning_unit_year_id)

            return HttpResponseRedirect(reverse('learning_unit', args=[learning_unit_year_id]))

        except IntegrityError as e:
            display_error_messages(request, e.args[0])

    context['form'] = form
    return layout.render(request, 'learning_unit/update_end_date.html', context)


def _get_current_learning_unit_year_id(learning_unit_to_edit, learning_unit_year_id):
    if not LearningUnitYear.objects.filter(pk=learning_unit_year_id).exists():
        result = LearningUnitYear.objects.filter(learning_unit=learning_unit_to_edit).last().pk
    else:
        result = learning_unit_year_id
    return result


@login_required
@permission_required('base.can_edit_learningunit', raise_exception=True)
@perms.can_perform_learning_unit_modification
def update_learning_unit(request, learning_unit_year_id):
    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    learning_unit_year_parent = learning_unit_year.parent
    person = get_object_or_404(Person, user=request.user)
    form = LearningUnitModificationForm(
        request.POST or None, learning_unit_year_instance=learning_unit_year, person=person)

    if form.is_valid():
        _save_form_and_display_messages(request, form)
        _check_credits(request, learning_unit_year_parent, form)
        return redirect("learning_unit", learning_unit_year_id=learning_unit_year.id)

    context = {"learning_unit_year": learning_unit_year, "form": form}
    return layout.render(request, 'learning_unit/modification.html', context)


@login_required
@permission_required('base.can_edit_learningunit', raise_exception=True)
@perms.can_perform_learning_unit_modification
def learning_unit_volumes_management(request, learning_unit_year_id):
    person = get_object_or_404(Person, user=request.user)
    context = get_common_context_learning_unit_year(learning_unit_year_id, person)

    context['learning_units'] = learning_unit_year_with_context.get_with_context(
        learning_container_year_id=context['learning_unit_year'].learning_container_year_id
    )

    volume_edition_formset_container = VolumeEditionFormsetContainer(request, context['learning_units'], person)

    if volume_edition_formset_container.is_valid() and not request.is_ajax():
        _save_form_and_display_messages(request, volume_edition_formset_container)
        return HttpResponseRedirect(reverse(learning_unit_components, args=[learning_unit_year_id]))

    context['formsets'] = volume_edition_formset_container.formsets
    context['tab_active'] = 'components'
    context['experimental_phase'] = True
    if request.is_ajax():
        return JsonResponse({'errors': volume_edition_formset_container.errors})

    return layout.render(request, "learning_unit/volumes_management.html", context)


def _save_form_and_display_messages(request, form):
    try:
        form.save()
        display_success_messages(request, _('success_modification_learning_unit'))
    except ConsistencyError as e:
        display_error_messages(request, e.error_list)
