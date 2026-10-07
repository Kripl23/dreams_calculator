from django import forms
from django.utils import timezone
from .models import Account, Contribution, Event


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'description', 'goal']


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['amount']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['date', 'amount']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.localdate():
            raise forms.ValidationError("Date can't be in the past")
        return date
