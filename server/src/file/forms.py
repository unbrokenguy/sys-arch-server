from django import forms


class UploadFileForm(forms.Form):
    description = forms.CharField(max_length=255, required=False)
    file = forms.FileField(required=False)
    user_input = forms.CharField(max_length=255, required=False)
