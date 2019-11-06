from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction
from .models import CATEGORY_CHOICES

class UserRegisterForm(UserCreationForm):

	class Meta:
		model = User
		fields = ['username', 'password1', 'password2']

class TransactionForm(forms.Form):
	tag = forms.CharField(max_length=100)
	amount = forms.DecimalField(max_digits=10,decimal_places=3)
	category = forms.CharField(max_length=7, widget=forms.Select(choices=CATEGORY_CHOICES))
	
	class Meta:
		model = Transaction
		exclude = ('user','date')
