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
from django import forms
from django.utils.translation import ugettext_lazy as _

from base.business.learning_unit_year_volumes import ENTITY_TYPES
from base.models.enums import entity_container_year_link_type as entity_types


class EmptyField(forms.CharField):
    widget = forms.HiddenInput

    def __init__(self, label):
        super().__init__(label=label, required=False)


class VolumeField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_digits=6, decimal_places=2, min_value=0, **kwargs)


class VolumeEditionForm(forms.Form):
    volume_total = VolumeField(label=_('total_volume_voltot'), help_text=_('total_volume'))
    equal_field_1 = EmptyField(label='=')
    volume_q1 = VolumeField(label=_('partial_volume_1Q'), help_text=_('partial_volume_1'))
    add_field = EmptyField(label='+')
    volume_q2 = VolumeField(label=_('partial_volume_2Q'), help_text=_('partial_volume_2'))
    mult_field = EmptyField(label='*')
    planned_classes = forms.IntegerField(label=_('planned_classes_pc'), help_text=_('planned_classes'), min_value=0)
    equal_field_2 = EmptyField(label='=')

    def __init__(self, *args, **kwargs):
        self.component = kwargs.pop('component')
        self.learning_unit_year = kwargs.pop('learning_unit_year')

        self.title = self.component.acronym
        self.title_help = _(self.component.type) + ' ' if self.component.type else ''
        self.title_help += self.component.acronym

        self.component_values = kwargs.pop('component_values')
        self.entities = kwargs.pop('entities')
        super().__init__(*args, **kwargs)

        for key, entity in self.entities.items():
            self.fields['volume_' + key.lower()] = VolumeField(
                label=entity.acronym, help_text=entity.title)

        self.fields['equal_field_3'] = EmptyField(label='=')

        self.fields['volume_total_requirement_entities'] = VolumeField(
            label=_('vol_charge'), help_text=_('total_volume_charge'))

        self.set_initial_values()

    def set_initial_values(self):
        for key, value in self.component_values.items():
            field = self.fields.get(key.lower())
            if field:
                self.fields[key.lower()].initial = value

    def clean(self):
        if not self._is_tot_annual_equal_to_q1_q2():
            self.add_error(None, "<b>{}/{}:</b> {}".format(
                self.learning_unit_year.acronym, self.component.acronym,
                _('vol_tot_not_equal_to_q1_q2')
            ))

        if not self._is_tot_req_entities_equal_to_vol_req_entity():
            error_msg = ' + '.join([
                self.entities.get(t).acronym for t in ENTITY_TYPES if self.entities.get(t)
            ])
            error_msg += ' = {}'.format(_('vol_charge'))
            self.add_error(None, "<b>{}/{}:</b> {}".format(
                self.learning_unit_year.acronym, self.component.acronym, error_msg))

        if not self._is_tot_req_entities_equal_to_tot_annual_mult_cp():
            self.add_error(None, "<b>{}/{}:</b> {}".format(
                self.learning_unit_year.acronym, self.component.acronym,
                _('vol_tot_req_entities_not_equal_to_vol_tot_mult_cp')))

    def _is_tot_annual_equal_to_q1_q2(self):
        total_annual = self.cleaned_data.get('volume_total', 0)
        q1 = self.cleaned_data.get('volume_q1', 0)
        q2 = self.cleaned_data.get('volume_q2', 0)
        return total_annual == (q1 + q2)

    def _is_tot_req_entities_equal_to_vol_req_entity(self):
        requirement_entity = self.cleaned_data.get(('volume_' + entity_types.REQUIREMENT_ENTITY).lower(), 0)
        additional_requirement_entity_1 = self.cleaned_data.get(('volume_' + entity_types.ADDITIONAL_REQUIREMENT_ENTITY_1).lower(), 0)
        additional_requirement_entity_2 = self.cleaned_data.get(('volume_' + entity_types.ADDITIONAL_REQUIREMENT_ENTITY_2).lower(), 0)
        total_requirement_entities = self.cleaned_data.get('volume_total_requirement_entities', 0)

        return total_requirement_entities == (
                requirement_entity + additional_requirement_entity_1 + additional_requirement_entity_2
        )

    def _is_tot_req_entities_equal_to_tot_annual_mult_cp(self):
        total_annual = self.cleaned_data.get('volume_total', 0)
        cp = self.cleaned_data.get('planned_classes', 0)
        total_requirement_entities = self.cleaned_data.get('volume_total_requirement_entities'.lower(), 0)
        return total_requirement_entities == (total_annual * cp)


class VolumeEditionBaseFormset(forms.BaseFormSet):

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year')
        self.components = list(self.learning_unit_year.components.keys())
        self.components_values = list(self.learning_unit_year.components.values())

        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['learning_unit_year'] = self.learning_unit_year
        kwargs['component'] = self.components[index]
        kwargs['component_values'] = self.components_values[index]
        kwargs['entities'] = self.learning_unit_year.entities
        return kwargs

    def save(self):
        for form in self.forms:
            form.save()
