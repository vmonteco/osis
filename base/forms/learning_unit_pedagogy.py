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
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.db.transaction import atomic
from django.forms import BaseInlineFormSet, inlineformset_factory

from base.business.learning_unit import find_language_in_settings, CMS_LABEL_PEDAGOGY
from base.business.learning_units.perms import can_edit_summary_locked_field
from base.forms.common import set_trans_txt
from base.models import academic_year, learning_unit_year, teaching_material
from base.models.learning_unit_year import LearningUnitYear
from base.models.teaching_material import TeachingMaterial
from cms.enums import entity_name
from cms.models import translated_text


class LearningUnitPedagogyForm(forms.Form):
    def __init__(self, *args, learning_unit_year=None, language_code=None, **kwargs):
        self.learning_unit_year = learning_unit_year
        self.language = find_language_in_settings(language_code)

        self.load_initial()
        super().__init__(*args, **kwargs)

    def load_initial(self):
        translated_texts_list = self._get_all_translated_text_related()
        set_trans_txt(self, translated_texts_list)

    def _get_all_translated_text_related(self):
        language_iso = self.language[0]

        return translated_text.search(entity=entity_name.LEARNING_UNIT_YEAR,
                                      reference=self.learning_unit_year.id,
                                      language=language_iso,
                                      text_labels_name=CMS_LABEL_PEDAGOGY)


class LearningUnitPedagogyEditForm(forms.Form):
    trans_text = forms.CharField(widget=CKEditorWidget(config_name='minimal_plus_headers'), required=False)
    cms_id = forms.IntegerField(widget=forms.HiddenInput, required=True)

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year', None)
        self.language_iso = kwargs.pop('language', None)
        self.text_label = kwargs.pop('text_label', None)
        super().__init__(*args, **kwargs)

    def load_initial(self):
        value = self._get_or_create_translated_text()
        self.fields['cms_id'].initial = value.id
        self.fields['trans_text'].initial = value.text

    @atomic
    def save(self):
        trans_text = self._get_or_create_translated_text()
        start_luy = learning_unit_year.get_by_id(trans_text.reference)

        reference_ids = [start_luy.id]
        if _is_pedagogy_data_must_be_postponed(start_luy):
            reference_ids += [luy.id for luy in start_luy.find_gt_learning_units_year()]

        for reference_id in reference_ids:
            translated_text.update_or_create(entity=trans_text.entity, reference=reference_id,
                                             language=trans_text.language, text_label=trans_text.text_label,
                                             text=self.cleaned_data['trans_text'])

    def _get_or_create_translated_text(self):
        if hasattr(self, 'cleaned_data'):
            cms_id = self.cleaned_data['cms_id']
            return translated_text.find_by_id(cms_id)
        return translated_text.get_or_create(
            entity=entity_name.LEARNING_UNIT_YEAR,
            reference=self.learning_unit_year.id,
            language=self.language_iso,
            text_label=self.text_label
        )


class SummaryModelForm(forms.ModelForm):
    def __init__(self, data, person, is_person_linked_to_entity, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        if not can_edit_summary_locked_field(person, is_person_linked_to_entity):
            self.fields["summary_locked"].disabled = True

        if not person.user.has_perm('base.can_edit_learningunit_pedagogy'):
            for field in self.fields.values():
                field.disabled = True

    class Meta:
        model = LearningUnitYear
        fields = ["summary_locked", 'bibliography', 'mobility_modality']

    @atomic
    def save(self, commit=True):
        instance = super().save(commit)
        if _is_pedagogy_data_must_be_postponed(instance):
            self._postpone_pedagogy_data(instance)
        return instance

    def _postpone_pedagogy_data(self, instance):
        for luy in instance.find_gt_learning_units_year():
            luy.mobility_modality = instance.mobility_modality
            luy.save()


def teachingmaterialformset_factory(can_edit=False):
    return inlineformset_factory(
        LearningUnitYear,
        TeachingMaterial,
        fields=('title', 'mandatory'),
        formset=TeachingMaterialFormsetPostponement,
        form=TeachingMaterialModelForm,
        max_num=10,
        extra=can_edit,
        can_delete=can_edit,
        labels={'title': ''}
    )


class TeachingMaterialFormsetPostponement(BaseInlineFormSet):
    @atomic
    def save(self, commit=True):
        instance_list = super().save(commit)
        luy = self.instance
        if _is_pedagogy_data_must_be_postponed(luy):
            teaching_material.postpone_teaching_materials(luy)
        return instance_list


class TeachingMaterialModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        person = kwargs.pop('person')
        super().__init__(*args, **kwargs)
        if not person.user.has_perm('base.can_edit_learningunit_pedagogy'):
            for field in self.fields.values():
                field.disabled = True


def _is_pedagogy_data_must_be_postponed(luy):
    # We must postpone pedagogy information, if we modify data form N+1
    current_academic_year = academic_year.current_academic_year()
    return luy.academic_year.year > current_academic_year.year
