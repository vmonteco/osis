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
from cms.enums import entity_name
from ckeditor.widgets import CKEditorWidget


class LearningAchievementEditForm(forms.Form):
    text = forms.CharField(widget=CKEditorWidget(config_name='minimal'), required=False)
    achievement_id = forms.IntegerField(widget=forms.HiddenInput, required=True)

    def __init__(self, *args, **kwargs):
        self.learning_achievement = kwargs.pop('learning_achievement', None)
        super(LearningAchievementEditForm, self).__init__(*args, **kwargs)

    def load_initial(self):
        self.fields['achievement_id'].initial = self.learning_achievement.id
        self.fields['text'].initial = self.learning_achievement.text

    def save(self):
        cleaned_data = self.cleaned_data
        achievement = learning_achievement.find_by_id(cleaned_data['achievement_id'])
        achievement.text = cleaned_data.get('text')
        achievement.save()
