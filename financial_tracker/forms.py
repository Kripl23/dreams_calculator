from django import forms
from .models import Account, Contribution


class AccountForms(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'description', 'goal']


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ['amount']
