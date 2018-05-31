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
import collections
import re

from django.http import Http404
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from base.models.academic_year import AcademicYear
from base.models.education_group_year import EducationGroupYear
from cms.models.text_label import TextLabel
from cms.models.translated_text import TranslatedText
from cms.models.translated_text_label import TranslatedTextLabel
from webservices.utils import convert_sections_to_list_of_dict

LANGUAGES = {'fr': 'fr-be', 'en': 'en'}
ENTITY = 'offer_year'

Context = collections.namedtuple(
    'Context',
    ['year', 'language', 'acronym',
     'title', 'description', 'translated_labels',
     'academic_year', 'education_group_year']
)


def find_translated_labels_for_entity_and_language(entity, language):
    queryset = TranslatedTextLabel.objects.filter(
        text_label__entity=entity, language=language)

    return {item.text_label.label: item.label for item in queryset}


def get_common_education_group(academic_year, language):
    education_group_year = EducationGroupYear.objects.filter(
        academic_year=academic_year, acronym__iexact='common').first()

    values = {}
    if education_group_year:
        queryset = TranslatedText.objects.filter(
            entity='offer_year',
            reference=education_group_year.id,
            language=language)

        for translated_text in queryset.order_by('text_label__order'):
            label = translated_text.text_label.label

            values[label] = translated_text

    return values


def get_cleaned_parameters(function):
    def inner_wrapper(request, year, language, acronym):
        year = to_int_or_404(year)

        if language not in LANGUAGES:
            raise Http404

        academic_year = get_object_or_404(AcademicYear, year=year)

        education_group_year = get_object_or_404(EducationGroupYear,
                                                 academic_year=academic_year,
                                                 acronym__iexact=acronym)
        iso_language = LANGUAGES[language]

        title = get_title_of_education_group_year(education_group_year, iso_language)
        translated_labels = find_translated_labels_for_entity_and_language(ENTITY, iso_language)
        description = new_description(education_group_year, language, title, year)

        context = Context(
            year=year,
            language=iso_language,
            acronym=acronym,
            title=title,
            academic_year=academic_year,
            education_group_year=education_group_year,
            translated_labels=translated_labels,
            description=description
        )

        return function(request, context)
    return inner_wrapper


def compute_sections_for_offer(context):
    sections = {}

    queryset = find_translated_texts_by_entity_and_language(
        context.education_group_year,
        ENTITY,
        context.language
    )

    for translated_text in queryset:
        insert_section(sections, translated_text, context)

    insert_common_sections(sections, context)

    return sections


def insert_common_sections(sections, context):
    common_terms = get_common_education_group(context.academic_year, context.language)

    common_sections = ['caap', 'agregations', 'prerequis', 'module_complementaire']
    for name in common_sections:
        common_name = '{name}-commun'.format(name=name)
        if name in sections and name in common_terms and common_name not in sections:
            term = common_terms[name]
            sections[common_name] = {
                'label': get_translated_label_from_translated_text(term, context.language),
                'content': term.text,
            }

def insert_section(sections, translated_text, context):
    name = translated_text.text_label.label

    sections[name] = {
        'label': get_translated_label_from_translated_text(translated_text, context.language),
        'content': translated_text.text
    }


def find_translated_texts_by_entity_and_language(education_group_year, entity, iso_language):
    queryset = TranslatedText.objects.filter(
        entity=entity,
        reference=education_group_year.id,
        language=iso_language)

    return queryset.order_by('text_label__order')


def new_description(education_group_year, language, title, year):
    return {
        'language': language,
        'acronym': education_group_year.acronym,
        'title': title,
        'year': year,
        'sections': [],
    }


def get_title_of_education_group_year(education_group_year, iso_language):
    if iso_language == 'fr-be':
        title = education_group_year.title
    else:
        title = education_group_year.title_english
    return title


def get_translated_label_from_translated_text(translated_text, language):
    record = TranslatedTextLabel.objects.get(text_label=translated_text.text_label,
                                             language=language)
    return record.label


INTRO_PATTERN = 'intro-(?P<acronym>\w+)'
COMMON_PATTERN = '(?P<section_name>\w+)-commun'


@api_view(['POST'])
@renderer_classes((JSONRenderer,))
# @get_cleaned_parameters(type_acronym='acronym')
# TODO: Ne pas oublier de verifier les params
def ws_catalog_offer(request, year, language, acronym):
    # Validation
    year = int(year)

    iso_language = LANGUAGES.get(language)
    if not iso_language:
        raise Http404

    education_group_year = get_object_or_404(EducationGroupYear,
                                             acronym__iexact=acronym,
                                             academic_year__year=year)

    title = get_title_of_education_group_year(education_group_year, iso_language)
    description = new_description(education_group_year, language, title, year)

    # Processing
    sections = collections.OrderedDict()

    items = request.data['sections']

    context = Context(
        acronym=acronym.upper(),
        year=year,
        title=title,
        description=description,
        translated_labels=None,
        education_group_year=education_group_year,
        academic_year=education_group_year.academic_year,
        language=iso_language,
    )

    for item in items:
        m_intro = re.match(INTRO_PATTERN, item)
        m_common = re.match(COMMON_PATTERN, item)
        if m_intro:
            egy = EducationGroupYear.objects.filter(partial_acronym__iexact=m_intro.group('acronym'),
                                                    academic_year__year=year).first()

            text_label = TextLabel.objects.filter(entity='offer_year', label='intro').first()
            if egy and text_label:
                ttl = TranslatedTextLabel.objects.filter(text_label=text_label,
                                                         language=context.language).first()

                tt = TranslatedText.objects.filter(text_label=text_label,
                                                   language=context.language,
                                                   entity=text_label.entity,
                                                   reference=egy.id).first()
                if ttl and tt:
                    sections[item] = {'label': ttl.label, 'content': tt.text}
                else:
                    sections[item] = {'label': ttl.label, 'content': None}
            else:
                sections[item] = {'label': None, 'content': None}
        elif not m_common:
            text_label = TextLabel.objects.filter(entity='offer_year', label=item).first()
            if not text_label:
                continue

            ttl = TranslatedTextLabel.objects.filter(text_label=text_label, language=context.language).first()
            tt = TranslatedText.objects.filter(text_label=text_label,
                                               language=context.language,
                                               entity=text_label.entity,
                                               reference=education_group_year.id).first()
            if ttl and tt:
                sections[item] = {'label': ttl.label, 'content': tt.text}
            elif ttl:
                sections[item] = {'label': ttl.label, 'content': None}

    insert_common_sections(sections, context)

    context.description['sections'] = convert_sections_to_list_of_dict(sections)
    return Response(context.description, content_type='application/json')
