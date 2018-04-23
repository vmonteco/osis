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

from base.models.learning_achievement import LearningAchievement, search
from reference.models.language import find_by_code

FR_CODE_LANGUAGE = 'FR'
EN_CODE_LANGUAGE = 'EN'


class LearningAchievementEditForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)

    class Meta:
        model = LearningAchievement
        fields = ['code_name', 'text']

    def save(self):
        super(LearningAchievementEditForm, self).save()
        learning_achievement_other_language = search(self.instance.learning_unit_year,
                                                     self.instance.order)
        if learning_achievement_other_language:
            learning_achievement_other_language.update(code_name=self.instance.code_name)


class LearningAchievementCreateForm(LearningAchievementEditForm):

    def save(self):
        super(LearningAchievementCreateForm, self).save()

        self._duplicate_other_language()

    def _duplicate_other_language(self):
        new_achievement = LearningAchievement(code_name=self.instance.code_name,
                                              learning_unit_year=self.instance.learning_unit_year,
                                              text=None,
                                              language=find_by_code(self._get_other_language()))
        new_achievement.save()

    def _get_other_language(self):
        return EN_CODE_LANGUAGE if self.instance.language.code == FR_CODE_LANGUAGE else FR_CODE_LANGUAGE
