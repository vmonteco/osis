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
from ckeditor.widgets import CKEditorWidget

from base.models.learning_achievement import LearningAchievement, find_learning_unit_achievement
from base.views import learning_achievement as learning_achievement_view

FR_CODE_LANGAGUE = 'FR'


class LearningAchievementEditForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)

    class Meta:
        model = LearningAchievement
        fields = ['code_name', 'text']

    def save(self, commit=True):
        super(LearningAchievementEditForm, self).save(commit)
        learning_achievement_other_language = \
            find_learning_unit_achievement(self.instance.learning_unit_year,
                                           _get_a_language_code(self.instance.language),
                                           self.instance.order)
        if learning_achievement_other_language:
            learning_achievement_other_language.code_name = self.instance.code_name
            learning_achievement_other_language.save()


def _get_a_language_code(a_language):
    if a_language.code == FR_CODE_LANGAGUE:
        return learning_achievement_view.EN_CODE_LANGAGUE
    return FR_CODE_LANGAGUE
