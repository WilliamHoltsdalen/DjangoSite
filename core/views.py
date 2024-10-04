from django.shortcuts import render, get_object_or_404
from .models import BankAccount, Transaction, Customer
from django.http import HttpResponseRedirect
from .forms import CustomerUpdateForm
from decimal import Decimal
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/dashboard/')
    return render(request, 'home.html')

def dashboard_view(request):

    if request.user.is_authenticated:
        context = {
            'transactions': request.user.customer.accounts.first().transactions.all()
        }   
        return render(request, 'dashboard.html', context)
    return HttpResponseRedirect('/login/')

def error_view(request):
    context={}
    return render(request, 'error.html', context)

def success_view(request):
    context={}
    return render(request, 'success.html', context)

def deposit_view(request):
    account = None
    if request.user.is_authenticated:   
        account = get_object_or_404(BankAccount, customer=request.user.customer)
    else:
        return render(request, 'error.html', {'message': 'Du er ikke logget inn!'})

    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        
        if account.deposit(amount):

            Transaction.objects.create(
                account=account,
                transaction_type='deposit',
                amount=amount,
                balance_after=account.balance
            )
            return render(request, 'success.html', {'message': 'Innskudd utført!'})
        return render(request, 'error.html', {'message': 'Beløp for innskudd må være større enn 0!'})
    return render(request, 'deposit.html')

def withdraw_view(request):
    account = None
    if request.user.is_authenticated:   
        account = get_object_or_404(BankAccount, customer=request.user.customer)
    else:
        return render(request, 'error.html', {'message': 'Du er ikke logget inn!'})

    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        if account.withdraw(amount):

            Transaction.objects.create(
                account=account,
                transaction_type='withdraw',
                amount=amount,
                balance_after=account.balance
            )
            return render(request, 'success.html', {'message': 'Uttak utført!'})
        return render(request, 'error.html', {'message': 'Utilstrekkelige midler!'})

    return render(request, 'withdraw.html')

def check_balance_view(request):
    account = None
    if request.user.is_authenticated:   
        account = get_object_or_404(BankAccount, customer=request.user.customer)
        return render(request, 'balance.html')
    return render(request, 'error.html', {'message': 'Kontonummer ikke funnet!'})
    

def update_customer_info_view(request):
    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.get(user=request.user)
    else:
        return render(request, 'error.html', {'message': 'Du er ikke logget inn!'})
    if request.method == "POST":
        customer.first_name = request.POST['first_name']
        customer.last_name = request.POST['last_name']
        customer.email = request.POST['email']
        customer.phone_number = request.POST['phone_number']
        customer.address = request.POST['address']
        customer.save()
        return render(request, 'profile_updated.html')
    return render(request, 'update_customer.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/home/')

def logout_view(request):
    logout(request)
    return render(request, 'logout.html')