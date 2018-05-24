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
from collections.__init__ import OrderedDict

from django import forms
from django.db import transaction
from django.forms import ModelChoiceField
from django.utils.translation import ugettext_lazy as _

from base.forms.learning_unit.learning_unit_create import LearningUnitModelForm, LearningUnitYearModelForm, \
    LearningContainerModelForm, EntitiesVersionChoiceField
from base.forms.learning_unit.learning_unit_create_2 import LearningUnitBaseForm, merge_data
from base.forms.utils.acronym_field import ExternalAcronymField
from base.models import entity_version
from base.models.campus import Campus
from base.models.entity_version import get_last_version, EntityVersion
from base.models.enums import learning_unit_year_subtypes
from base.models.enums.learning_container_year_types import EXTERNAL
from base.models.external_learning_unit_year import ExternalLearningUnitYear
from base.models.learning_container_year import LearningContainerYear
from reference.models import language
from reference.models.country import Country


class CampusChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}".format(obj.organization.name)


class LearningContainerYearExternalModelForm(forms.ModelForm):
    country = ModelChoiceField(queryset=Country.objects.all().order_by('name'), required=False, label=_("country"))
    campus = CampusChoiceField(queryset=Campus.objects.none())

    def __init__(self, *args, **kwargs):
        kwargs.pop('person')
        kwargs.pop('proposal')
        super().__init__(*args, **kwargs)

        self.fields['campus'].queryset = Campus.objects.order_by('organization__name').distinct('organization__name')
        self.fields["container_type"].choices = ((EXTERNAL, _(EXTERNAL)),)

    class Meta:
        model = LearningContainerYear
        fields = ('container_type', 'common_title', 'common_title_english', 'language', 'campus',
                  'type_declaration_vacant', 'team', 'is_vacant')

    def save(self, **kwargs):
        self.instance.learning_container = kwargs.pop('learning_container')
        self.instance.acronym = kwargs.pop('acronym')
        self.instance.academic_year = kwargs.pop('academic_year')
        return super().save(**kwargs)

    def post_clean(self, specific_title):
        if not self.instance.common_title and not specific_title:
            self.add_error("common_title", _("must_set_common_title_or_specific_title"))

        return not self.errors


class LearningUnitExternalModelForm(forms.ModelForm):
    buyer = EntitiesVersionChoiceField(queryset=EntityVersion.objects.none())
    entity_version = None

    def __init__(self, data, person, *args, **kwargs):
        self.person = person

        super().__init__(data, *args, **kwargs)
        self.fields['buyer'].queryset = self.person.find_main_entities_version
        self.fields['external_credits'].label = _('local_credits')

        if hasattr(self.instance, 'buyer'):
            self.initial['buyer'] = get_last_version(self.instance.buyer)

    class Meta:
        model = ExternalLearningUnitYear
        fields = ('external_acronym', 'external_credits', 'url', 'buyer')

    def clean_buyer(self):
        ev_data = self.cleaned_data['buyer']
        self.entity_version = ev_data
        return ev_data.entity if ev_data else None

    def post_clean(self, start_date):
        entity = self.cleaned_data.get('buyer')
        if not entity:
            return True

        entity_v = entity_version.get_by_entity_and_date(entity, start_date)
        if not entity_v:
            self.add_error('buyer', _("The linked entity does not exist at the start date of the "
                                      "academic year linked to this learning unit"))
        else:
            self.entity_version = entity_v

        return not self.errors

    def save(self, commit=True):
        self.instance.author = self.person
        return super().save(commit)


class LearningUnitExternalForm(LearningUnitBaseForm):
    forms = OrderedDict()
    academic_year = None
    subtype = learning_unit_year_subtypes.FULL

    entity_version = None

    form_cls_to_validate = [
        LearningUnitModelForm,
        LearningUnitYearModelForm,
        LearningContainerModelForm,
        LearningContainerYearExternalModelForm,
        LearningUnitExternalModelForm
    ]

    def __init__(self, person, academic_year=None, data=None, *args, **kwargs):
        self.academic_year = academic_year
        self.person = person
        instances_data = self._build_instance_data(data, academic_year, None)
        super().__init__(instances_data, *args, **kwargs)
        self.disable_fields('container_type')
        self.learning_unit_year_form.fields['acronym'] = ExternalAcronymField()

    @property
    def learning_unit_external_form(self):
        return self.forms[LearningUnitExternalModelForm]

    @property
    def learning_container_year_form(self):
        return self.forms[LearningContainerYearExternalModelForm]

    def _build_instance_data(self, data, default_ac_year, proposal):
        return {
            LearningUnitModelForm: {
                'data': merge_data(data, {'start_year': default_ac_year.year, 'periodicity': 'ANNUAL'}),
                'instance': self.instance.learning_unit if self.instance else None,
            },
            LearningContainerModelForm: {
                'data': data,
                'instance': self.instance.learning_container_year.learning_container if self.instance else None,
            },
            LearningUnitYearModelForm: self._build_instance_data_learning_unit_year(data, default_ac_year),
            LearningContainerYearExternalModelForm: self._build_instance_data_learning_container_year(data, proposal),
            LearningUnitExternalModelForm: self._build_instance_data_external_learning_unit(data)
        }

    def _build_instance_data_external_learning_unit(self, data):
        return {
            'data': data,
            'instance': None,
            'person': self.person
        }

    def _build_instance_data_learning_unit_year(self, data, default_ac_year):
        return {
            'data': merge_data(data, {'periodicity': 'ANNUAL'}),
            'instance': self.instance,
            'initial': {'status': True,
                        'academic_year': default_ac_year},
            'person': self.person,
            'subtype': self.subtype
        }

    def _build_instance_data_learning_unit(self, data, inherit_lu_values):
        return {
            'data': merge_data(data, inherit_lu_values),
            'instance': None,
            'initial': inherit_lu_values if not self.instance else None,
        }

    def _build_instance_data_learning_container_year(self, data, proposal):
        return {
            'data': data,
            'instance': self.instance.learning_container_year if self.instance else None,
            'proposal': proposal,
            'initial': {
                # Default language French
                'language': language.find_by_code('FR'),
            },
            'person': self.person
        }

    def get_context(self):
        return {
            'subtype': self.subtype,
            'learning_unit_form': self.learning_unit_form,
            'learning_unit_year_form': self.learning_unit_year_form,
            'learning_container_year_form': self.learning_container_year_form,
            'learning_unit_external_form': self.learning_unit_external_form
        }

    @transaction.atomic()
    def save(self, commit=True):
        academic_year = self.academic_year

        learning_container = self.learning_container_form.save(commit)
        learning_unit = self.learning_unit_form.save(
            start_year=self.learning_unit_year_form.instance.academic_year.year,
            learning_container=learning_container,
            commit=commit
        )
        container_year = self.learning_container_year_form.save(
            academic_year=academic_year,
            learning_container=learning_container,
            acronym=self.learning_unit_year_form.instance.acronym,
            commit=commit
        )

        # Save learning unit year (learning_unit_component +  learning_component_year + entity_component_year)
        learning_unit_year = self.learning_unit_year_form.save(
            learning_container_year=container_year,
            learning_unit=learning_unit,
            entity_container_years=[],
            commit=commit
        )

        self.learning_unit_external_form.instance.learning_unit_year = learning_unit_year
        self.learning_unit_external_form.save(commit)

        return learning_unit_year

    def is_valid(self):
        return super().is_valid() and self.learning_unit_external_form.post_clean(self.academic_year.start_date)
