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

from ckeditor.fields import RichTextFormField
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django import forms
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from prettyprinter import cpprint
from waffle.decorators import waffle_flag

from base import models as mdl
from base.business import education_group as education_group_business
from base.business.education_group import assert_category_of_education_group_year
from base.forms.education_group_pedagogy_edit import EducationGroupPedagogyEditForm
from base.forms.education_groups_administrative_data import CourseEnrollmentForm, AdministrativeDataFormset
from base.models.admission_condition import AdmissionConditionLine, AdmissionCondition
from base.models.education_group_year import EducationGroupYear
from base.models.enums import academic_calendar_type
from base.models.enums import education_group_categories
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


def education_group_year_pedagogy_edit_post(request, education_group_year_id, root_id):
    form = EducationGroupPedagogyEditForm(request.POST)

    if form.is_valid():
        label = form.cleaned_data['label']

        text_label = TextLabel.objects.filter(label=label).first()

        record, created = TranslatedText.objects.get_or_create(reference=str(education_group_year_id),
                                                               entity='offer_year',
                                                               text_label=text_label,
                                                               language='fr-be')
        record.text = form.cleaned_data['text_french']
        record.save()

        record, created = TranslatedText.objects.get_or_create(reference=str(education_group_year_id),
                                                               entity='offer_year',
                                                               text_label=text_label,
                                                               language='en')
        record.text = form.cleaned_data['text_english']
        record.save()

    redirect_url = reverse('education_group_general_informations', kwargs={
        'root_id': root_id,
        'education_group_year_id': education_group_year_id
    })

    return redirect(redirect_url)


def education_group_year_pedagogy_edit_get(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    context = {
        'education_group_year': education_group_year,
    }
    label_name = request.GET.get('label')
    initial_values = {'label': label_name}
    fr_text = TranslatedText.objects.filter(reference=str(education_group_year_id),
                                            text_label__label=label_name,
                                            entity=entity_name.OFFER_YEAR,
                                            language='fr-be').first()
    if fr_text:
        initial_values['text_french'] = fr_text.text
    en_text = TranslatedText.objects.filter(reference=str(education_group_year_id),
                                            text_label__label=label_name,
                                            entity=entity_name.OFFER_YEAR,
                                            language='en').first()
    if en_text:
        initial_values['text_english'] = en_text.text
    form = EducationGroupPedagogyEditForm(initial=initial_values)
    context['form'] = form
    context['group_to_parent'] = request.GET.get("group_to_parent") or '0'
    return layout.render(request, 'education_group/pedagogy_edit.html', context)


@login_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def education_group_year_pedagogy_edit(request, root_id, education_group_year_id):
    if request.method == 'POST':
        return education_group_year_pedagogy_edit_post(request, education_group_year_id, root_id)

    return education_group_year_pedagogy_edit_get(request, education_group_year_id)


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


# keep
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


# keep
@login_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_remove_line(request, root_id, education_group_year_id):
    admission_condition_line_id = request.GET['id']

    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    admission_condition = get_object_or_404(AdmissionCondition, education_group_year=education_group_year)
    admission_condition_line = get_object_or_404(AdmissionConditionLine,
                                                 admission_condition=admission_condition,
                                                 pk=admission_condition_line_id)
    admission_condition_line.delete()
    return redirect(reverse('education_group_year_admission_condition_edit',
                            kwargs={'root_id': root_id, 'education_group_year_id': education_group_year_id}))


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


class Form(forms.Form):
    admission_condition_line = forms.IntegerField(widget=forms.HiddenInput())
    section = forms.CharField(widget=forms.HiddenInput())
    language = forms.CharField(widget=forms.HiddenInput())
    diploma = forms.CharField(widget=forms.Textarea, required=False)
    conditions = forms.CharField(widget=forms.Textarea, required=False)
    access = forms.CharField(widget=forms.Textarea, required=False)
    remarks = forms.CharField(widget=forms.Textarea, required=False)


def education_group_year_admission_condition_update_line_post(request, root_id, education_group_year_id):
    creation_mode = request.POST.get('admission_condition_line') == ''

    if creation_mode:
        # bypass the validation of the form
        request.POST = request.POST.copy()
        request.POST.update({'admission_condition_line': 0})

    form = Form(request.POST)

    if form.is_valid():
        admission_condition_line_id = form.cleaned_data['admission_condition_line']
        language = form.cleaned_data['language']
        lang = '' if language == 'fr' else '_en'

        if not creation_mode:
            admission_condition_line = get_object_or_404(AdmissionConditionLine,
                                                         pk=admission_condition_line_id)
        else:
            section = form.cleaned_data['section']
            education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
            admission_condition_line = AdmissionConditionLine.objects.create(
                admission_condition=education_group_year.admissioncondition,
                section=section)

        for key in ('diploma', 'conditions', 'access', 'remarks'):
            setattr(admission_condition_line, key + lang, form.cleaned_data[key])

        admission_condition_line.save()

    return redirect(
        reverse('education_group_year_admission_condition_edit', args=[root_id, education_group_year_id])
    )


def education_group_year_admission_condition_update_line_get(request):
    section = request.GET['section']
    language = request.GET['language']
    lang = '' if language == 'fr' else '_en'

    initial_values = {
        'language': language,
        'section': section,
    }

    admission_condition_line_id = request.GET.get('id')

    if admission_condition_line_id:
        admission_condition_line = get_object_or_404(AdmissionConditionLine,
                                                     pk=admission_condition_line_id,
                                                     section=section)

        initial_values['admission_condition_line'] = admission_condition_line.id

        response = get_content_of_admission_condition_line('read', admission_condition_line, lang)
        initial_values.update(response)

    form = Form(initial=initial_values)

    context = {
        'form': form
    }
    return layout.render(request, 'education_group/condition_line_edit.html', context)


@login_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_update_line(request, root_id, education_group_year_id):
    if request.method == 'POST':
        return education_group_year_admission_condition_update_line_post(request, root_id, education_group_year_id)
    return education_group_year_admission_condition_update_line_get(request)


class UpdateTextForm(forms.Form):
    # text = forms.CharField(widget=forms.Textarea)
    text = RichTextFormField(required=False, config_name='minimal')
    section = forms.CharField(widget=forms.HiddenInput())
    language = forms.CharField(widget=forms.HiddenInput())


def education_group_year_admission_condition_update_text_post(request, root_id, education_group_year_id):
    form = UpdateTextForm(request.POST)

    if form.is_valid():
        education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
        language = form.cleaned_data['language']
        lang = '' if language == 'fr' else '_en'
        section = form.cleaned_data['section']

        admission_condition = education_group_year.admissioncondition

        setattr(admission_condition, 'text_' + section + lang, form.cleaned_data['text'])
        admission_condition.save()

    return redirect(
        reverse('education_group_year_admission_condition_edit', args=[root_id, education_group_year_id])
    )


def education_group_year_admission_condition_update_text_get(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    section = request.GET['section']
    language = request.GET['language']
    lang = '' if language == 'fr' else '_en'

    form = UpdateTextForm(initial={
        'section': section,
        'language': language,
        'text': getattr(education_group_year.admissioncondition, 'text_' + section + lang)
    })

    context = {
        'form': form,
    }
    return layout.render(request, 'education_group/condition_text_edit.html', context)


@login_required
@permission_required('base.can_edit_educationgroup_pedagogy', raise_exception=True)
def education_group_year_admission_condition_update_text(request, root_id, education_group_year_id):
    if request.method == 'POST':
        return education_group_year_admission_condition_update_text_post(request, root_id, education_group_year_id)
    return education_group_year_admission_condition_update_text_get(request, education_group_year_id)
