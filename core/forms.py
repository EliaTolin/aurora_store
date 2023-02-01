from django import forms

from core.models import App

PAYMENT_CHOICES = (
    ('P', 'PayPal: pagamenti@paypal.com'),
    ('B', 'Bonifico: IT324349874327432084L'),
)

'''
Form for checkout
'''


class CheckoutForm(forms.Form):
    country = forms.CharField(required=False)
    city = forms.CharField(required=False)
    route = forms.CharField(required=False)
    cap = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'CAP'}))
    house_number = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Numero Civico'}))
    note = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Note'}))
    save_info = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    opzioni_pagamento = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    email = forms.CharField(required=True)


class RaitingForm(forms.Form):
    raiting = forms.IntegerField(
        required=True, max_value=5, min_value=0)

    class Meta:
        model = App
        fields = ['raiting']
