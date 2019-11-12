from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import UserRegisterForm, TransactionForm
from django.contrib.auth.models import User
from .models import Transaction, Profile
from django.views.generic import View
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Q
from django.contrib import messages
import datetime
import json

# Create your views here.

def register(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			messages.success(request,f'Your account has been created. Please log-in.')
			return redirect('login')
	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html',{'form':form})

@login_required
def profile(request):

	if request.method == 'GET':

		results = Transaction.objects.all()

		query = request.GET.get('q')
		start = request.GET.get('start')
		end = request.GET.get('end')
		print(start)

		if query and query!="":
			results = results.filter(Q(tag__icontains=query))

		if start and start!="":
			results = results.filter(Q(date__gte=start))

		if end and end!="":
			results = results.filter(Q(date__lte=end))

		context = {
			'transactions' : results,
			'profiles' : Profile.objects.all()


		}
		
		return render(request, 'users/profile.html', context)


	elif request.method == 'DELETE':
		id = json.loads(request.body)['id']
		transaction = get_object_or_404(Transaction,id=id)
		transaction.delete()

		return HttpResponse('')
		

	return HttpResponseRedirect(reverse('profile'))

@login_required
def statistics(request):
    return render(request, 'users/statistics.html')
@login_required
def howto(request):
	return render(request, 'users/howto.html')

def get_data(request):

    dataset = Transaction.objects \
        .values('category') \
        .exclude(category='') \
        .annotate(total=Count('category',filter=(Q(user=request.user)))) \
        .order_by('category')

    profile = Profile(user=request.user)
    income = float(profile.total_income())
    expenses = float(profile.total_expenses())*-1
    for i in range(len(dataset)):
    	if i==0:
    		dataset[i].update(total=expenses)
    	else:
    		dataset[i].update(total=income)
    print(dataset)
    category_display_name = {
        "Income":"Income",
        "Expense":"Expense"
    }

    chart = {
        'chart': {'type': 'pie'},
        'title': {'text': 'PayUP'},
        'series': [{
            'name': 'Total',
            'data': list(map(lambda row: {'name': category_display_name[row['category']], 'y': row['total']}, dataset))
        }]
    }


    return JsonResponse(chart)

@login_required
def home(request):
	context = {
		'transactions' : Transaction.objects.all(),
		'profiles' : Profile.objects.all()
	}


	if request.method == 'POST':
		
		income_list = Transaction.objects.filter(Q(category="Income")).values('tag')
		expense_list = Transaction.objects.filter(Q(category="Expense")).values('tag')
		inc = []
		exp = []
		for i in income_list:
			for k, v in i.items():
				if v not in inc:
					inc.append(v)
		for i in expense_list:
			for k, v in i.items():
				if v not in exp:
					exp.append(v)
		
		form = TransactionForm(request.POST)
		if form.is_valid():
			tag = form.cleaned_data.get('tag')
			amount = form.cleaned_data.get('amount')
			category = form.cleaned_data.get('category')
			user=request.user
			""" def clean(self, value):
    			cleaned_data = self.cleaned_data
				if category=='Expense' and tag in inc:
					raise forms.ValidationError("You call that a title?!")
				else:
					return cleaned_data 
				if category=='Income' and tag in exp:
					raise forms.ValidationError("You call that a title?!")
				else:
					return cleaned_data  """
			if category=='Expense' and tag in inc:
				#return render(request, 'users/home.html', {'some_flag': True})
				messages.warning(request, 'This tag already exists as an income.')
			elif category=='Income' and tag in exp:
				#return render(request, 'users/home.html', {'some_flag': True})
				messages.warning(request, 'This tag already exists as an expense.')
			 
			Transaction.objects.create(
				user=user,
				tag=tag,
				amount=amount,
				category=category
			).save()

	return render(request, 'users/home.html', context)