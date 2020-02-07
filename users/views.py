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

    category_display_name = {
        "Income":"Income",
        "Expense":"Expense"
    }

    chart = {
        'chart': {'type': 'pie'},
        'title': {'text': 'Financial Statistics'},
        'colors': ['#36D137','#36A9D1'],
        'plotOptions': {
        	'pie' : {
		        'dataLabels': {
		            'enabled': False
		         },
		        'showInLegend': True
		    }
	    },
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
		
		form = TransactionForm(request.POST)
		if form.is_valid():
			tag = form.cleaned_data.get('tag')
			amount = form.cleaned_data.get('amount')
			category = form.cleaned_data.get('category')
			user=request.user
			 
			Transaction.objects.create(
				user=user,
				tag=tag,
				amount=amount,
				category=category
			).save()

	return render(request, 'users/home.html', context)