from django import forms
from rest_api.models import UserInput, File


class UploadFileForm(forms.ModelForm):

    class Meta:
        model = File
        fields = ['file']


class UploadUserInputForm(forms.ModelForm):

    class Meta:
        model = UserInput
        fields = ['value']
