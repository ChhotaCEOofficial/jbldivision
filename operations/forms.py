from django import forms
from .models import MeBasicEntry, StatsMonthlyEntry

class ReportUploadForm(forms.Form):
    file = forms.FileField()

class MeBasicForm(forms.ModelForm):
    class Meta:
        model = MeBasicEntry
        fields = '__all__'

class StatsMonthlyForm(forms.ModelForm):
    class Meta:
        model = StatsMonthlyEntry
        fields = '__all__'