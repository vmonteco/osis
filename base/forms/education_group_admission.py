from ckeditor.fields import RichTextFormField
from django import forms


class UpdateLineForm(forms.Form):
    admission_condition_line = forms.IntegerField(widget=forms.HiddenInput())
    section = forms.CharField(widget=forms.HiddenInput())
    language = forms.CharField(widget=forms.HiddenInput())
    diploma = forms.CharField(widget=forms.Textarea, required=False)
    conditions = forms.CharField(widget=forms.Textarea, required=False)
    access = forms.CharField(widget=forms.Textarea, required=False)
    remarks = forms.CharField(widget=forms.Textarea, required=False)


class UpdateTextForm(forms.Form):
    text = RichTextFormField(required=False, config_name='minimal')
    section = forms.CharField(widget=forms.HiddenInput())
    language = forms.CharField(widget=forms.HiddenInput())