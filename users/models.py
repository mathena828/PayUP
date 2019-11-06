from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
# Create your models here.

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)

	def total_balance(self):
		transaction_list = self.user.transaction_set.all()
		total_balance_amount = 0
		for transaction in transaction_list:
			if transaction.category=='Income':
				total_balance_amount += transaction.amount
			elif transaction.category=='Expense':
				total_balance_amount -= transaction.amount
		return total_balance_amount

	def total_income(self):
		transaction_list = self.user.transaction_set.all()
		total_income_amount = 0
		for transaction in transaction_list:
			if transaction.category=='Income':
				total_income_amount += transaction.amount
		return total_income_amount
	

	def total_expenses(self):
		transaction_list = self.user.transaction_set.all()
		total_expenses_amount = 0
		for transaction in transaction_list:
			if transaction.category=='Expense':
				total_expenses_amount -= transaction.amount
		return total_expenses_amount

CATEGORY_CHOICES = (
		('income','Income'),
		('expense','Expense'),
)

class Transaction(models.Model):
	
	user=models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
	category = models.CharField(max_length=7, choices=CATEGORY_CHOICES, default='income')
	date = models.DateTimeField(default=timezone.now)
	tag = models.CharField(max_length=100)
	amount = models.DecimalField(max_digits=10,decimal_places=2)

	

	class Meta:
		ordering = ('-date',)
	

