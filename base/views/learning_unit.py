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

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http import QueryDict
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods, require_POST, require_GET

from attribution.business import attribution_charge_new
from base import models as mdl
from base.business import learning_unit_deletion, learning_unit_year_volumes, learning_unit_year_with_context, \
    learning_unit_proposal
from base.business.learning_unit import create_learning_unit, create_learning_unit_structure, \
    get_common_context_learning_unit_year, get_cms_label_data, \
    extract_volumes_from_data, get_same_container_year_components, get_components_identification, show_subtype, \
    get_organization_from_learning_unit_year, get_campus_from_learning_unit_year, \
    get_all_attributions, get_last_academic_years, \
    SIMPLE_SEARCH, SERVICE_COURSES_SEARCH, create_xls, is_summary_submission_opened, find_language_in_settings, \
    initialize_learning_unit_pedagogy_form, compute_max_academic_year_adjournment, \
    create_learning_unit_partim_structure, can_access_summary
from base.forms.common import TooManyResultsException
from base.forms.learning_units import LearningUnitYearForm
from base.models import entity_container_year
from base.models import proposal_learning_unit, entity_version
from base.models.enums import learning_container_year_types, learning_unit_year_subtypes
from base.models.enums.learning_unit_year_subtypes import FULL
from base.models.learning_container import LearningContainer

from base.forms.learning_unit_create import CreateLearningUnitYearForm, EMPTY_FIELD, CreatePartimForm, \
    PARTIM_FORM_READ_ONLY_FIELD
from base.forms.learning_unit_specifications import LearningUnitSpecificationsForm, LearningUnitSpecificationsEditForm
from base.forms.learning_unit_pedagogy import LearningUnitPedagogyEditForm
from base.forms.learning_unit_component import LearningUnitComponentEditForm
from base.forms.learning_class import LearningClassEditForm
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from cms.models import text_label
from reference.models import language
from . import layout
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.conf import settings


CMS_LABEL_SPECIFICATIONS = ['themes_discussed', 'skills_to_be_acquired', 'prerequisite']
CMS_LABEL_PEDAGOGY = ['resume', 'bibliography', 'teaching_methods', 'evaluation_methods',
                      'other_informations', 'online_resources']
CMS_LABEL_SUMMARY = ['resume']


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units(request):
    return _learning_units_search(request, SIMPLE_SEARCH)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units_service_course(request):
    return _learning_units_search(request, SERVICE_COURSES_SEARCH)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_identification(request, learning_unit_year_id):
    person = get_object_or_404(Person, user=request.user)
    context = get_common_context_learning_unit_year(learning_unit_year_id)
    learning_unit_year = context['learning_unit_year']
    context['learning_container_year_partims'] = learning_unit_year.get_partims_related()
    context['organization'] = get_organization_from_learning_unit_year(learning_unit_year)
    context['campus'] = get_campus_from_learning_unit_year(learning_unit_year)
    context['experimental_phase'] = True
    context['show_subtype'] = show_subtype(learning_unit_year)
    context.update(get_all_attributions(learning_unit_year))
    context['components'] = get_components_identification(learning_unit_year)
    context['can_propose'] = learning_unit_proposal.is_eligible_for_modification_proposal(learning_unit_year, person)
    context['proposal'] = proposal_learning_unit.find_by_learning_unit_year(learning_unit_year)
    context['can_cancel_proposal'] = learning_unit_proposal.\
        is_eligible_for_cancel_of_proposal(context['proposal'], person) if context['proposal'] else False
    context['proposal_folder_entity_version'] = \
        entity_version.get_by_entity_and_date(context['proposal'].folder.entity, None) if context['proposal'] else None
    context['can_delete'] = learning_unit_deletion.can_delete_learning_unit_year(person, learning_unit_year)

    return layout.render(request, "learning_unit/identification.html", context)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_formations(request, learning_unit_year_id):
    context = get_common_context_learning_unit_year(learning_unit_year_id)
    return layout.render(request, "learning_unit/formations.html", context)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_components(request, learning_unit_year_id):
    context = get_common_context_learning_unit_year(learning_unit_year_id)
    context['components'] = get_same_container_year_components(context['learning_unit_year'], True)
    context['tab_active'] = 'components'
    context['experimental_phase'] = True
    return layout.render(request, "learning_unit/components.html", context)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def volumes_validation(request, learning_unit_year_id):
    volumes_encoded = extract_volumes_from_data(request.POST.dict())
    volumes_grouped_by_lunityear = learning_unit_year_volumes.get_volumes_grouped_by_lunityear(learning_unit_year_id,
                                                                                               volumes_encoded)
    return JsonResponse({
        'errors': learning_unit_year_volumes.validate(volumes_grouped_by_lunityear)
    })


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_volumes_management(request, learning_unit_year_id):
    if request.method == 'POST':
        _learning_unit_volumes_management_edit(request, learning_unit_year_id)

    context = get_common_context_learning_unit_year(learning_unit_year_id)
    context['learning_units'] = learning_unit_year_with_context.get_with_context(
        learning_container_year_id=context['learning_unit_year'].learning_container_year_id
    )
    context['tab_active'] = 'components'
    context['experimental_phase'] = True
    return layout.render(request, "learning_unit/volumes_management.html", context)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_pedagogy(request, learning_unit_year_id):
    context = get_common_context_learning_unit_year(learning_unit_year_id)
    learning_unit_year = context['learning_unit_year']

    user_language = mdl.person.get_user_interface_language(request.user)
    context['cms_labels_translated'] = get_cms_label_data(CMS_LABEL_PEDAGOGY, user_language)

    context['form_french'] = initialize_learning_unit_pedagogy_form(learning_unit_year, settings.LANGUAGE_CODE_FR)
    context['form_english'] = initialize_learning_unit_pedagogy_form(learning_unit_year, settings.LANGUAGE_CODE_EN)
    context['experimental_phase'] = True
    return layout.render(request, "learning_unit/pedagogy.html", context)


@login_required
@permission_required('base.can_edit_learningunit_pedagogy', raise_exception=True)
@require_http_methods(["GET", "POST"])
def learning_unit_pedagogy_edit(request, learning_unit_year_id):
    if request.method == 'POST':
        form = LearningUnitPedagogyEditForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse("learning_unit_pedagogy",
                                            kwargs={'learning_unit_year_id': learning_unit_year_id}))

    context = get_common_context_learning_unit_year(learning_unit_year_id)
    label_name = request.GET.get('label')
    language = request.GET.get('language')
    text_lb = text_label.find_root_by_name(label_name)
    form = LearningUnitPedagogyEditForm(**{
        'learning_unit_year': context['learning_unit_year'],
        'language': language,
        'text_label': text_lb
    })
    form.load_initial()  # Load data from database
    context['form'] = form

    user_language = mdl.person.get_user_interface_language(request.user)
    context['text_label_translated'] = next((txt for txt in text_lb.translated_text_labels
                                             if txt.language == user_language), None)
    context['language_translated'] = find_language_in_settings(language)
    return layout.render(request, "learning_unit/pedagogy_edit.html", context)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_attributions(request, learning_unit_year_id):
    context = get_common_context_learning_unit_year(learning_unit_year_id)
    context['attribution_charge_news'] = \
        attribution_charge_new.find_attribution_charge_new_by_learning_unit_year(
            learning_unit_year=learning_unit_year_id)
    context['experimental_phase'] = True
    return layout.render(request, "learning_unit/attributions.html", context)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_unit_specifications(request, learning_unit_year_id):
    context = get_common_context_learning_unit_year(learning_unit_year_id)
    learning_unit_year = context['learning_unit_year']

    user_language = mdl.person.get_user_interface_language(request.user)
    context['cms_labels_translated'] = get_cms_label_data(CMS_LABEL_SPECIFICATIONS, user_language)

    fr_language = find_language_in_settings(settings.LANGUAGE_CODE_FR)
    en_language = find_language_in_settings(settings.LANGUAGE_CODE_EN)

    context.update({
        'form_french': LearningUnitSpecificationsForm(learning_unit_year, fr_language),
        'form_english': LearningUnitSpecificationsForm(learning_unit_year, en_language)
    })
    context['experimental_phase'] = True
    return layout.render(request, "learning_unit/specifications.html", context)


@login_required
@permission_required('base.can_edit_learningunit_specification', raise_exception=True)
@require_http_methods(["GET", "POST"])
def learning_unit_specifications_edit(request, learning_unit_year_id):
    if request.method == 'POST':
        form = LearningUnitSpecificationsEditForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse("learning_unit_specifications",
                                            kwargs={'learning_unit_year_id': learning_unit_year_id}))

    context = get_common_context_learning_unit_year(learning_unit_year_id)
    label_name = request.GET.get('label')
    text_lb = text_label.find_root_by_name(label_name)
    language = request.GET.get('language')
    form = LearningUnitSpecificationsEditForm(**{
        'learning_unit_year': context['learning_unit_year'],
        'language': language,
        'text_label': text_lb
    })
    form.load_initial()  # Load data from database
    context['form'] = form

    user_language = mdl.person.get_user_interface_language(request.user)
    context['text_label_translated'] = next((txt for txt in text_lb.translated_text_labels
                                             if txt.language == user_language), None)
    context['language_translated'] = find_language_in_settings(language)
    return layout.render(request, "learning_unit/specifications_edit.html", context)


@login_required
@permission_required('base.change_learningcomponentyear', raise_exception=True)
@require_http_methods(["GET", "POST"])
def learning_unit_component_edit(request, learning_unit_year_id):
    context = get_common_context_learning_unit_year(learning_unit_year_id)
    learning_component_id = request.GET.get('learning_component_year_id')
    context['learning_component_year'] = mdl.learning_component_year.find_by_id(learning_component_id)

    if request.method == 'POST':
        form = LearningUnitComponentEditForm(request.POST,
                                             learning_unit_year=context['learning_unit_year'],
                                             instance=context['learning_component_year'])
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse(learning_unit_components,
                                            kwargs={'learning_unit_year_id': learning_unit_year_id}))

    form = LearningUnitComponentEditForm(learning_unit_year=context['learning_unit_year'],
                                         instance=context['learning_component_year'])
    form.load_initial()  # Load data from database
    context['form'] = form
    return layout.render(request, "learning_unit/component_edit.html", context)


@login_required
@permission_required('base.change_learningclassyear', raise_exception=True)
@require_http_methods(["GET", "POST"])
def learning_class_year_edit(request, learning_unit_year_id):
    context = get_common_context_learning_unit_year(learning_unit_year_id)
    context.update(
        {'learning_class_year': mdl.learning_class_year.find_by_id(request.GET.get('learning_class_year_id')),
         'learning_component_year':
             mdl.learning_component_year.find_by_id(request.GET.get('learning_component_year_id'))})

    if request.method == 'POST':
        form = LearningClassEditForm(
            request.POST,
            instance=context['learning_class_year'],
            learning_unit_year=context['learning_unit_year'],
            learning_component_year=context['learning_component_year']
        )
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse("learning_unit_components",
                                            kwargs={'learning_unit_year_id': learning_unit_year_id}))

    form = LearningClassEditForm(
        instance=context['learning_class_year'],
        learning_unit_year=context['learning_unit_year'],
        learning_component_year=context['learning_component_year']
    )
    form.load_initial()  # Load data from database
    context['form'] = form
    return layout.render(request, "learning_unit/class_edit.html", context)


@login_required
@permission_required('base.can_create_learningunit', raise_exception=True)
def learning_unit_create(request, academic_year):
    person = get_object_or_404(Person, user=request.user)
    form = CreateLearningUnitYearForm(person, initial={'academic_year': academic_year,
                                                       'subtype': FULL,
                                                       "container_type": EMPTY_FIELD,
                                                       'language': language.find_by_code('FR')})
    return layout.render(request, "learning_unit/learning_unit_form.html", {'form': form})


@login_required
@permission_required('base.can_create_learningunit', raise_exception=True)
@require_POST
def learning_unit_year_add(request):
    person = get_object_or_404(Person, user=request.user)
    form = CreateLearningUnitYearForm(person, request.POST)
    if form.is_valid():
        data = form.cleaned_data
        year = data['academic_year'].year
        status = data['status'] == 'on'
        additional_requirement_entity_1 = data.get('additional_requirement_entity_1')
        additional_requirement_entity_2 = data.get('additional_requirement_entity_2')
        allocation_entity_version = data.get('allocation_entity')
        requirement_entity_version = data.get('requirement_entity')
        campus = data.get('campus')

        new_learning_container = LearningContainer.objects.create()
        new_learning_unit = create_learning_unit(data, new_learning_container, year)
        academic_year_max = compute_max_academic_year_adjournment()
        while year < academic_year_max:
            academic_year = mdl.academic_year.find_academic_year_by_year(year)

            create_learning_unit_structure(additional_requirement_entity_1, additional_requirement_entity_2,
                                           allocation_entity_version, data, new_learning_container,
                                           new_learning_unit, requirement_entity_version, status, academic_year, campus)
            year += 1
        success_msg = _('learning_unit_successfuly_created').format(data['acronym'], academic_year_max)
        messages.add_message(request, messages.SUCCESS, success_msg)
        return redirect('learning_units')
    else:
        return layout.render(request, "learning_unit/learning_unit_form.html", {'form': form})


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def check_acronym(request):
    acronym = request.GET['acronym']
    year_id = request.GET['year_id']
    academic_yr = mdl.academic_year.find_academic_year_by_id(year_id)
    valid = True
    existed_acronym = False
    existing_acronym = False
    last_using = ""

    learning_unit_years = mdl.learning_unit_year.find_gte_year_acronym(academic_yr, acronym)
    old_learning_unit_year = mdl.learning_unit_year.find_lt_year_acronym(academic_yr, acronym).last()

    if old_learning_unit_year:
        last_using = str(old_learning_unit_year.academic_year)
        existed_acronym = True

    if learning_unit_years:
        existing_acronym = True
        valid = False

    return JsonResponse({'valid': valid,
                         'existing_acronym': existing_acronym,
                         'existed_acronym': existed_acronym,
                         'last_using': last_using}, safe=False)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units_activity(request):
    return _learning_units_search(request, SIMPLE_SEARCH)


@login_required
@permission_required('base.can_access_learningunit', raise_exception=True)
def learning_units_service_course(request):
    return _learning_units_search(request, SERVICE_COURSES_SEARCH)


def _learning_units_search(request, search_type):
    service_course_search = search_type == SERVICE_COURSES_SEARCH
    request_get = request.GET if request.GET.get('academic_year_id') else None

    form = LearningUnitYearForm(request_get, service_course_search=service_course_search)

    found_learning_units = []
    try:
        if form.is_valid():
            found_learning_units = form.get_activity_learning_units()

            _check_if_display_message(request, found_learning_units)
    except TooManyResultsException:
        messages.add_message(request, messages.ERROR, _('too_many_results'))

    if request.GET.get('xls_status') == "xls":
        return create_xls(request.user, found_learning_units)

    context = {
        'form': form,
        'academic_years': get_last_academic_years(),
        'container_types': learning_container_year_types.LEARNING_CONTAINER_YEAR_TYPES,
        'types': learning_unit_year_subtypes.LEARNING_UNIT_YEAR_SUBTYPES,
        'learning_units': found_learning_units,
        'current_academic_year': mdl.academic_year.current_academic_year(),
        'experimental_phase': True,
        'search_type': search_type
    }
    return layout.render(request, "learning_units.html", context)


def _check_if_display_message(request, found_learning_units):
    if not found_learning_units:
        messages.add_message(request, messages.WARNING, _('no_result'))
    return True


def _learning_unit_volumes_management_edit(request, learning_unit_year_id):
    errors = None
    volumes_encoded = extract_volumes_from_data(request.POST.dict())

    try:
        errors = learning_unit_year_volumes.update_volumes(learning_unit_year_id, volumes_encoded)
    except Exception as e:
        error_msg = e.messages[0] if isinstance(e, ValidationError) else e.args[0]
        messages.add_message(request, messages.ERROR, _(error_msg))

    if errors:
        for error_msg in errors:
            messages.add_message(request, messages.ERROR, error_msg)


@login_required
def learning_unit_summary(request, learning_unit_year_id):
    if not is_summary_submission_opened():
        return redirect(reverse_lazy('outside_summary_submission_period'))
    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    if not can_access_summary(request.user, learning_unit_year):
        raise PermissionDenied("User is not summary responsible")

    user_language = mdl.person.get_user_interface_language(request.user)
    return layout.render(request, "my_osis/educational_information.html", {
        'learning_unit_year': learning_unit_year,
        'cms_labels_translated': get_cms_label_data(CMS_LABEL_SUMMARY, user_language),
        'form_french': initialize_learning_unit_pedagogy_form(learning_unit_year, settings.LANGUAGE_CODE_FR),
        'form_english': initialize_learning_unit_pedagogy_form(learning_unit_year, settings.LANGUAGE_CODE_EN)
    })


@login_required
@require_http_methods(["GET", "POST"])
def summary_edit(request, learning_unit_year_id):
    if not is_summary_submission_opened():
        return redirect(reverse_lazy("outside_summary_submission_period"))

    learning_unit_year = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    if not can_access_summary(request.user, learning_unit_year):
        raise PermissionDenied("User is not summary responsible")

    if request.method == 'POST':
        form = LearningUnitPedagogyEditForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("learning_unit_summary", learning_unit_year_id=learning_unit_year_id)
    label_name = request.GET.get('label')
    lang = request.GET.get('language')
    text_lb = text_label.find_root_by_name(label_name)
    form = LearningUnitPedagogyEditForm(**{'learning_unit_year': learning_unit_year, 'language': lang,
                                           'text_label': text_lb})
    form.load_initial()
    user_language = mdl.person.get_user_interface_language(request.user)
    text_label_translated = next((txt for txt in text_lb.translated_text_labels if txt.language == user_language), None)
    return layout.render(request, "my_osis/educational_information_edit.html", {
        "learning_unit_year": learning_unit_year,
        "form": form,
        "language_translated": find_language_in_settings(lang),
        "text_label_translated": text_label_translated
    })

@login_required
def outside_period(request):
    text = _('summary_responsible_denied')
    messages.add_message(request, messages.WARNING, "%s" % text)
    return render(request, "access_denied.html")


@login_required
@permission_required('base.can_create_learningunit', raise_exception=True)
@require_GET
def learning_unit_create_partim(request, learning_unit_year_id):
    person = get_object_or_404(Person, user=request.user)
    learning_unit_year_parent = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)
    initial = compute_partim_form_initial_data(learning_unit_year_parent)
    return layout.render(request, "learning_unit/partim_form.html", {'form': CreatePartimForm(person, initial=initial)})


@login_required
@permission_required('base.can_create_learningunit', raise_exception=True)
@require_POST
def learning_unit_year_partim_add(request, learning_unit_year_id):
    person = get_object_or_404(Person, user=request.user)
    learning_unit_year_parent = get_object_or_404(LearningUnitYear, pk=learning_unit_year_id)

    initial = compute_partim_form_initial_data(learning_unit_year_parent)
    post_data = _get_post_data_without_read_only_field(request.POST.copy())

    post_data_merged = QueryDict('', mutable=True)
    post_data_merged.update(initial)
    post_data_merged.update(post_data)
    form = CreatePartimForm(person, post_data_merged)
    if form.is_valid():
        create_partim_process(learning_unit_year_parent, form)
        return HttpResponseRedirect(reverse("learning_unit",
                                            kwargs={'learning_unit_year_id': learning_unit_year_parent.id}))
    return layout.render(request, "learning_unit/partim_form.html", {'form': form})


def _get_post_data_without_read_only_field(post_data):
    post_data_without_read_only = post_data.copy()
    for read_only_field in PARTIM_FORM_READ_ONLY_FIELD:
        post_data_without_read_only.pop(read_only_field, None)
    return post_data_without_read_only


def create_partim_process(learning_unit_year_parent, form):
    data = form.cleaned_data
    academic_year = data['academic_year']
    start_year = academic_year.year
    end_year = learning_unit_year_parent.learning_unit.end_year

    learning_container = learning_unit_year_parent.learning_container_year.learning_container
    learning_unit_created = create_learning_unit(data, learning_container, start_year, end_year)

    create_partim_process_on_years(data, learning_unit_created, learning_container, end_year)


def create_partim_process_on_years(data, new_learning_unit, learning_container, end_year_learning_unit_parent):
    academic_year = data['academic_year']
    year = academic_year.year
    status = data['status']
    additional_requirement_entity_version_1 = data.get('additional_requirement_entity_1')
    additional_requirement_entity_version_2 = data.get('additional_requirement_entity_2')
    allocation_entity_version = data.get('allocation_entity')
    requirement_entity_version = data.get('requirement_entity')
    academic_year_max = compute_max_academic_year_adjournment()

    while (year < academic_year_max) and (not end_year_learning_unit_parent or year <= end_year_learning_unit_parent):
        academic_year = mdl.academic_year.find_academic_year_by_year(year)
        create_learning_unit_partim_structure({
            'requirement_entity_version': requirement_entity_version,
            'additional_requirement_entity_version_1': additional_requirement_entity_version_1,
            'additional_requirement_entity_version_2': additional_requirement_entity_version_2,
            'allocation_entity_version': allocation_entity_version,
            'data': data,
            'learning_container': learning_container,
            'new_learning_unit': new_learning_unit,
            'status': status,
            'academic_year': academic_year
        })
        year += 1


def compute_partim_form_initial_data(learning_unit_year_parent):
    initial = compute_form_initial_data(learning_unit_year_parent)
    initial['subtype'] = learning_unit_year_subtypes.PARTIM
    return initial


def compute_form_initial_data(learning_unit_year):
    initial_data = {
        "academic_year": learning_unit_year.academic_year.id,
        "first_letter": learning_unit_year.acronym[0],
        "acronym": learning_unit_year.acronym[1:],
        "subtype": learning_unit_year.subtype,
        "container_type": learning_unit_year.learning_container_year.container_type,
        "language": learning_unit_year.learning_container_year.language.id,
        "status": learning_unit_year.status,
        "credits": learning_unit_year.credits,
        "title": learning_unit_year.title,
        "title_english": learning_unit_year.title_english,
        'session': learning_unit_year.session,
        'faculty_remark': learning_unit_year.learning_unit.faculty_remark,
        'other_remark': learning_unit_year.learning_unit.other_remark,
        "periodicity": learning_unit_year.learning_unit.periodicity,
        "quadrimester": learning_unit_year.quadrimester,
        "campus": learning_unit_year.learning_container_year.campus.id,
        "internship_subtype": learning_unit_year.internship_subtype
    }
    attributions = entity_container_year.find_last_entity_version_grouped_by_linktypes(
        learning_unit_year.learning_container_year
    )
    initial_data.update({k.lower(): v.id for k, v in attributions.items()})
    return {key: value for key, value in initial_data.items() if value is not None}
