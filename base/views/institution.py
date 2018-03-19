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
import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from base import models as mdl
from base.business.institution.perms import can_user_edit_educational_information_submission_dates_for_entity
from base.forms.entity_calendar import EntityCalendarEducationalInformationForm
from base.models import entity_version as entity_version_mdl
from base.models.entity_calendar import find_by_entity_and_reference_for_current_academic_year
from base.models.entity_version import EntityVersion
from base.models.enums import entity_type, academic_calendar_type
from . import layout

logger = logging.getLogger(settings.DEFAULT_LOGGER)


@login_required
@permission_required('base.is_institution_administrator', raise_exception=True)
def institution(request):
    return layout.render(request, "institution.html", {'section': 'institution'})


@login_required
@permission_required('base.can_access_mandate', raise_exception=True)
def mandates(request):
    return layout.render(request, "mandates.html", {'section': 'mandates'})


@login_required
def academic_actors(request):
    return layout.render(request, "academic_actors.html", {})


@login_required
def entities(request):
    return layout.render(request, "entities.html", {'init': "0",
                                                    'types': entity_type.ENTITY_TYPES})


@login_required
def entities_search(request):
    entities_version = mdl.entity_version.search_entities(acronym=request.GET.get('acronym'),
                                                          title=request.GET.get('title'),
                                                          type=request.GET.get('type_choices'),
                                                          with_entity=True)
    return layout.render(request, "entities.html", {'entities_version': entities_version,
                                                    'init': "1",
                                                    'types': entity_type.ENTITY_TYPES})


@login_required
def entity_read(request, entity_version_id):
    entity_version = get_object_or_404(EntityVersion, id=entity_version_id)
    can_user_edit = can_user_edit_educational_information_submission_dates_for_entity(request.user,
                                                                                      entity_version.entity)
    if request.method == "POST" and not can_user_edit:
        logger.warning("User {} has no sufficient right to modify submission dates of educational information.".
                       format(request.user))
        raise PermissionDenied()

    entity_parent = entity_version.get_parent_version()
    descendants = entity_version.descendants
    entity_calendar_instance = find_by_entity_and_reference_for_current_academic_year(
        entity_version.entity.id, academic_calendar_type.SUMMARY_COURSE_SUBMISSION)

    form = EntityCalendarEducationalInformationForm(request.POST or None, instance=entity_calendar_instance)
    if form.is_valid():
        form.save_entity_calendar(entity_version.entity)

    return layout.render(request, "entity/identification.html", locals())


@login_required
def entities_version(request, entity_version_id):
    entity_version = mdl.entity_version.find_by_id(entity_version_id)
    entity_parent = entity_version.get_parent_version()
    entities_version = mdl.entity_version.search(entity=entity_version.entity)\
                                         .order_by('-start_date')
    return layout.render(request, "entity/versions.html", locals())


@login_required
def entity_diagram(request, entity_version_id):
    entity_version = mdl.entity_version.find_by_id(entity_version_id)
    entities_version_as_json = json.dumps(entity_version.get_organogram_data(level=0))
    return layout.render(request, "entity/organogram.html", locals())


@login_required
def get_entity_address(request, entity_version_id):
    version = entity_version_mdl.find_by_id(entity_version_id)
    entity = version.entity
    response = {
        'entity_version_exists_now': version.exists_now(),
        'recipient': '{} - {}'.format(version.acronym, version.title),
        'address': {}
    }
    if entity and entity.has_address():
        response['address'] = {'location': entity.location,
                               'postal_code': entity.postal_code,
                               'city': entity.city,
                               'country_id': entity.country_id,
                               'phone': entity.phone,
                               'fax': entity.fax,
                               }
    return JsonResponse(response)
