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
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse

from attribution.models.attribution import Attribution
from base.business.learning_unit import get_cms_label_data, initialize_learning_unit_pedagogy_form, CMS_LABEL_SUMMARY
from base.models import person
from base.models.tutor import is_tutor
from base.views import layout


@login_required
@user_passes_test(is_tutor)
def list_my_attributions(request):
    context = {}
    return layout.render(request, 'manage_my_courses/list_my_attributions.html', context)


@login_required
def manage_educational_information(request, attribution_id):
    attribution = Attribution.objects.get(pk=attribution_id)
    learning_unit_year = attribution.learning_unit_year
    user_language = person.get_user_interface_language(request.user)
    return layout.render(request, 'manage_my_courses/educational_information.html', {
        "learning_unit_year": learning_unit_year,
        'cms_labels_translated': get_cms_label_data(CMS_LABEL_SUMMARY, user_language),
        'form_french': initialize_learning_unit_pedagogy_form(learning_unit_year, settings.LANGUAGE_CODE_FR),
        'form_english': initialize_learning_unit_pedagogy_form(learning_unit_year, settings.LANGUAGE_CODE_EN)
    })