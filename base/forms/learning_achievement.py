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

from base.forms.common import set_trans_txt
from base.models import learning_achievement
from base.models.learning_achievement import LearningAchievement, find_learning_unit_achievement
from cms.enums import entity_name
from ckeditor.widgets import CKEditorWidget


class LearningAchievementEditForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)

    class Meta:
        model = LearningAchievement
        fields = ['code_name', 'text']

    def __init__(self, *args, **kwargs):
        self.learning_unit_year = kwargs.pop('learning_unit_year', None)
        super(LearningAchievementEditForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(LearningAchievementEditForm, self).save(commit=False)
        learning_achievement_other_language = \
            find_learning_unit_achievement(self.instance.learning_unit_year,
                                           _get_a_language_code(self.instance.language),
                                           self.instance.order)
        if learning_achievement_other_language:
            learning_achievement_other_language.code_name = self.instance.code_name
            learning_achievement_other_language.save()

        if commit:
            instance.save()
        return instance


def _get_a_language_code(a_language):
    if a_language.code == 'FR':
        return 'EN'
    else:
        return 'FR'
