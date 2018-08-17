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

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from waffle.decorators import waffle_flag

from base import models as mdl
from base.business import education_group as education_group_business
from base.business.education_group import assert_category_of_education_group_year
from base.business.learning_unit import find_language_in_settings
from base.forms.education_group_pedagogy_edit import EducationGroupPedagogyEditForm
from base.forms.education_groups_administrative_data import CourseEnrollmentForm, AdministrativeDataFormset
from base.models.admission_condition import AdmissionConditionLine, AdmissionCondition
from base.models.education_group_year import EducationGroupYear
from base.models.enums import academic_calendar_type
from base.models.enums import education_group_categories
from base.views.learning_units.common import get_text_label_translated
from cms.enums import entity_name
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from osis_common.decorators.ajax import ajax_required
from . import layout


@login_required
@waffle_flag("education_group_update")
@permission_required('base.can_edit_education_group_administrative_data', raise_exception=True)
def education_group_edit_administrative_data(request, root_id, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    assert_category_of_education_group_year(education_group_year, (education_group_categories.TRAINING,))

    if not education_group_business.can_user_edit_administrative_data(request.user, education_group_year):
        raise PermissionDenied("Only program managers of the education group OR central manager "
                               "linked to entity can edit.")

    formset_session = AdministrativeDataFormset(request.POST or None,
                                                form_kwargs={'education_group_year': education_group_year})

    offer_year_calendar = mdl.offer_year_calendar.search(
        education_group_year_id=education_group_year_id,
        academic_calendar_reference=academic_calendar_type.COURSE_ENROLLMENT).first()

    course_enrollment = CourseEnrollmentForm(request.POST or None, instance=offer_year_calendar)

    course_enrollment_validity = course_enrollment.is_valid()
    formset_session_validity = formset_session.is_valid()

    group_to_parent = request.GET.get("group_to_parent")

    if course_enrollment_validity and formset_session_validity:
        formset_session.save()
        course_enrollment.save()
        messages.add_message(request, messages.SUCCESS, _('The administrative data has been successfully modified'))
        return HttpResponseRedirect(reverse('education_group_administrative', args=[root_id, education_group_year_id]))

    return layout.render(request, "education_group/tab_edit_administrative_data.html", locals())


def find_root_by_name(text_label_name):
    return TextLabel.objects.prefetch_related(
        Prefetch('translatedtextlabel_set', to_attr="translated_text_labels")
    ).get(label=text_label_name, parent__isnull=True)


def education_group_year_pedagogy_edit_post(request, root_id, education_group_year_id):
    form = EducationGroupPedagogyEditForm(request.POST)
    if form.is_valid():
        form.save()
    redirect_url = reverse('education_group_general_informations', args=[root_id, education_group_year_id])
    return redirect(redirect_url)


@login_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def education_group_year_pedagogy_edit(request, root_id, education_group_year_id):
    if request.method == 'POST':
        return education_group_year_pedagogy_edit_post(request, root_id, education_group_year_id)

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    context = {
        'education_group_year': education_group_year,
    }

    label_name = request.GET.get('label')
    language = request.GET.get('language')

    text_lb = find_root_by_name(label_name)
    form = EducationGroupPedagogyEditForm(**{
        'education_group_year': context['education_group_year'],
        'language': language,
        'text_label': text_lb,
    })

    form.load_initial()
    context['form'] = form
    user_language = mdl.person.get_user_interface_language(request.user)
    context['text_label_translated'] = get_text_label_translated(text_lb, user_language)
    context['language_translated'] = find_language_in_settings(language)
    context['group_to_parent'] = request.GET.get("group_to_parent") or '0'

    return layout.render(request, 'education_group/pedagogy_edit.html', context)


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_pedagogy_add_term(request, root_id, education_group_year_id):

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    label = request.GET.get('label')
    text_label = get_object_or_404(TextLabel, label=label, entity=entity_name.OFFER_YEAR)

    translated_text_ids = {
        'label': text_label.label,
    }

    for language in ('fr-be', 'en'):
        translated_text = TranslatedText.objects.create(text_label=text_label,
                                                        reference=education_group_year.id,
                                                        language=language,
                                                        entity=entity_name.OFFER_YEAR)

        translated_text_label = TranslatedTextLabel.objects.get(text_label=text_label, language=language)

        translated_text_ids[language] = {
            'id': translated_text_label.id,
            'translation': translated_text_label.label,
        }

    return JsonResponse({'message': 'added', 'translated_texts': translated_text_ids})


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_pedagogy_remove_term(request, root_id, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    label = request.GET.get('label')
    text_label = get_object_or_404(TextLabel, label=label, entity=entity_name.OFFER_YEAR)
    translated_texts = TranslatedText.objects.filter(text_label=text_label,
                                                     reference=education_group_year.id,
                                                     entity=entity_name.OFFER_YEAR)
    translated_texts.delete()
    return JsonResponse({'education_group_year': int(education_group_year.pk)})


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_pedagogy_get_terms(request, root_id, education_group_year_id, language):
    text_labels = TextLabel.objects.filter(entity='offer_year')

    translated_texts = TranslatedText.objects.filter(text_label__entity=entity_name.OFFER_YEAR,
                                                     reference=str(education_group_year_id),
                                                     entity=entity_name.OFFER_YEAR)

    unique_has_for_this_egy = set(item.text_label for item in translated_texts)
    unique_text_labels = set(item for item in text_labels)

    text_labels_to_load = unique_text_labels - unique_has_for_this_egy

    translated_text_labels = TranslatedTextLabel.objects.filter(language=language,
                                                                text_label_id__in=text_labels_to_load,
                                                                text_label__entity=entity_name.OFFER_YEAR)

    records = list(map(translated_text_labels2dict, translated_text_labels.order_by('text_label__label')))

    return JsonResponse({'records': records})


def translated_text_labels2dict(translated_text_label):
    return {
        'id': translated_text_label.id,
        'language': translated_text_label.language,
        'label': translated_text_label.text_label.label,
        'translation': translated_text_label.label
    }


@login_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_edit(request, root_id, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    parent = get_object_or_404(EducationGroupYear, pk=root_id)

    acronym = education_group_year.acronym.lower()

    is_common = acronym.startswith('common-')
    is_specific = not is_common

    is_master = acronym.endswith(('2m', '2m1'))
    use_standard_text = acronym.endswith(('2a', '2mc'))

    class AdmissionConditionForm(forms.Form):
        text_field = forms.CharField(widget=CKEditorWidget(config_name='minimal'))

    admission_condition_form = AdmissionConditionForm()

    admission_condition, created = AdmissionCondition.objects.get_or_create(
        education_group_year=education_group_year)

    record = {}
    for section in ('ucl_bachelors', 'others_bachelors_french', 'bachelors_dutch', 'foreign_bachelors',
                    'graduates', 'masters'):
        record[section] = AdmissionConditionLine.objects.filter(admission_condition=admission_condition,
                                                                section=section)

    context = {
        'admission_condition_form': admission_condition_form,
        'education_group_year': education_group_year,
        'parent': parent,
        'root': parent,
        'root_id': parent.id,

        'can_edit_information': request.user.has_perm('base.can_edit_educationgroup_pedagogy'),
        'info': {
            'is_specific': is_specific,
            'is_common': is_common,
            'is_bachelor': acronym == 'common-bacs',
            'is_master': is_master,
            'show_components_for_agreg_and_mc': is_common and use_standard_text,
            'show_free_text': is_specific and (is_master or use_standard_text),
        },
        'admission_condition': admission_condition,
        'record': record,
        'group_to_parent': request.GET.get("group_to_parent"),
    }

    return layout.render(request, 'education_group/tab_admission_conditions.html', context)


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_add_line(request, root_id, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    info = json.loads(request.body.decode('utf-8'))

    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)

    admission_condition_line = AdmissionConditionLine.objects.create(
        admission_condition=admission_condition,
        section=info['section'],
        diploma=info['diploma'],
        conditions=info['conditions'],
        access=info['access'],
        remarks=info['remarks']
    )

    record = {
        'id': admission_condition_line.id,
        'section': admission_condition_line.section,
        'diploma': admission_condition_line.diploma,
        'conditions': admission_condition_line.conditions,
        'access': admission_condition_line.access,
        'remarks': admission_condition_line.remarks,
    }
    return JsonResponse({'message': 'added', 'record': record})


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_remove_line(request, root_id, education_group_year_id):
    info = json.loads(request.body.decode('utf-8'))
    admission_condition_line_id = info['id']

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    admission_condition = get_object_or_404(AdmissionCondition, education_group_year=education_group_year)
    admission_condition_line = get_object_or_404(AdmissionConditionLine,
                                                 admission_condition=admission_condition,
                                                 pk=admission_condition_line_id)
    admission_condition_line.delete()
    return JsonResponse({'message': 'deleted'})


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_modify_text(request, root_id, education_group_year_id):
    info = json.loads(request.body.decode('utf-8'))
    lang = '' if info['language'] == 'fr' else '_en'

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)

    column = 'text_{}{}'.format(info['section'], lang)
    setattr(admission_condition, column, info['text'])
    admission_condition.save()
    admission_condition.refresh_from_db()

    response = {
        'message': 'updated',
        'text': getattr(admission_condition, column, '')
    }
    return JsonResponse(response)


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_get_text(request, root_id, education_group_year_id):
    info = json.loads(request.body.decode('utf-8'))
    lang = '' if info['language'] == 'fr' else '_en'

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)
    column = 'text_' + info['section'] + lang
    text = getattr(admission_condition, column, 'Undefined')
    return JsonResponse({'message': 'read', 'section': info['section'], 'text': text})


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_get_line(request, root_id, education_group_year_id):

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)

    info = json.loads(request.body.decode('utf-8'))
    lang = '' if info['language'] == 'fr' else '_en'

    admission_condition_line = get_object_or_404(AdmissionConditionLine,
                                                 admission_condition=admission_condition,
                                                 section=info['section'],
                                                 pk=info['id'])

    response = get_content_of_admission_condition_line('read', admission_condition_line, lang)
    return JsonResponse(response)


def get_content_of_admission_condition_line(message, admission_condition_line, lang):
    return {
        'message': message,
        'section': admission_condition_line.section,
        'id': admission_condition_line.id,
        'diploma': getattr(admission_condition_line, 'diploma' + lang, ''),
        'conditions': getattr(admission_condition_line, 'conditions' + lang, ''),
        'access': getattr(admission_condition_line, 'access' + lang, ''),
        'remarks': getattr(admission_condition_line, 'remarks' + lang, ''),
    }


@login_required
@ajax_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_update_line(request, root_id, education_group_year_id):

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)

    admission_condition, created = AdmissionCondition.objects.get_or_create(education_group_year=education_group_year)

    info = json.loads(request.body.decode('utf-8'))

    admission_condition_line = get_object_or_404(AdmissionConditionLine,
                                                 admission_condition=admission_condition,
                                                 section=info.pop('section'),
                                                 pk=info.pop('id')
                                                 )

    lang = '' if info['language'] == 'fr' else '_en'

    for key, value in info.items():
        setattr(admission_condition_line, key + lang, value)

    admission_condition_line.save()

    admission_condition_line.refresh_from_db()

    response = get_content_of_admission_condition_line('updated', admission_condition_line, lang)
    return JsonResponse(response)
