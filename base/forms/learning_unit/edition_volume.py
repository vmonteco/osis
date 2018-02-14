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
from django.forms import formset_factory
from django.utils.translation import ugettext_lazy as _


class VolumeEditionForm(forms.Form):
    volume_total = forms.FloatField(label=_('total_volume_voltot'), help_text=_('total_volume'))
    volume_q1 = forms.FloatField(label=_('partial_volume_1Q'), help_text=_('partial_volume_1'))
    volume_q2 = forms.FloatField(label=_('partial_volume_2Q'), help_text=_('partial_volume_2'))
    planned_classes = forms.IntegerField(label=_('planned_classes_pc'), help_text=_('planned_classes'))

    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop('title')
        self.component = kwargs.pop('component_values')
        self.entities = kwargs.pop('entities')
        super().__init__(*args, **kwargs)

        for key, entity in self.entities.items():
            self.fields['volume_' + key.lower()] = forms.FloatField(label=entity.acronym, help_text=entity.title)

        self.fields['volume_total_requirement_entities'] = forms.FloatField(label=_('vol_charge'),
                                                                            help_text=_('total_volume_charge'))

        for key, value in self.component.items():
            field = self.fields.get(key.lower())
            if not field:
                continue

            self.fields[key.lower()].inital = value


class VolumeEditionBaseFormset(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year')
        self.components = list(self.learning_unit_year.components.keys())
        self.components_values = list(self.learning_unit_year.components.values())

        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['title'] = self.components[index].acronym
        kwargs['component_values'] = self.components_values[index]
        kwargs['entities'] = self.learning_unit_year.entities
        return kwargs

    def save(self):
        for form in self.forms:
            form.save()


VolumeEditionFormset = formset_factory(
    form=VolumeEditionForm,
    formset=VolumeEditionBaseFormset,
    extra=1
)






