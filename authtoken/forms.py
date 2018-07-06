from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from .models import InventoryToken
from api.models import Inventory


class ScopedTokenForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ScopedTokenForm, self).__init__(*args, **kwargs)
        self.fields['inventory'].queryset = Inventory.objects.filter(user=user)

    class Meta:
        model = InventoryToken
        fields = ('inventory', 'description')
        widgets = {
            'inventory':  CheckboxSelectMultiple()
        }
