from .forms import CustomerForm, BankAccountForm, AddressBookForm
from .models import BankAccount, Transaction, Customer, AddressBook
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/dashboard/')
    return render(request, 'home.html')

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

def dashboard_view(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        accounts = customer.accounts.all()
        transactions = Transaction.objects.filter(account__in=accounts)
        context = {
            'transactions': transactions,
            'accounts': accounts,
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
    if request.user.is_authenticated:
        customer = request.user.customer
        accounts = customer.accounts.all()  # Hent alle kontoene til kunden

        context = {
            'accounts': accounts,
        }

        if request.method == 'POST':
            account_id = request.POST.get('account_id')  # Hent valgt konto fra skjemaet
            amount = Decimal(request.POST['amount'])
            account = get_object_or_404(BankAccount, id=account_id, customer=customer)

            if account.deposit(amount):
                # Opprett en transaksjon
                Transaction.objects.create(
                    account=account,
                    transaction_type='deposit',
                    amount=amount,
                    balance_after=account.balance
                )
                messages.success(request, 'Innskudd utført!')
                return redirect('deposit')
            messages.error(request, 'Beløp for innskudd må være større enn 0!')
            return redirect('deposit')
        return render(request, 'deposit.html', context)

def withdraw_view(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        accounts = customer.accounts.all()  # Hent alle kontoene til kunden

        context = {
            'accounts': accounts,
        }

        if request.method == 'POST':
            account_id = request.POST.get('account_id')  # Hent valgt konto fra skjemaet
            amount = Decimal(request.POST['amount'])
            account = get_object_or_404(BankAccount, id=account_id, customer=customer)

            if account.withdraw(amount):
                # Opprett en transaksjon
                Transaction.objects.create(
                    account=account,
                    transaction_type='withdraw',
                    amount=amount,
                    balance_after=account.balance
                )
                messages.success(request, 'Uttak utført!')
                return redirect('withdraw')
            messages.success(request, 'Utilstrekkelige midler!')
            return redirect('withdraw')
        return render(request, 'withdraw.html', context)


def check_balance_view(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        accounts = customer.accounts.all()
        context = {
            'accounts': accounts,
        }
        return render(request, 'balance.html', context)
    return render(request, 'error.html', {'message': 'Du er ikke logget inn!'})

    

@login_required
def account_settings_view(request):
    customer = request.user.customer
    bank_accounts = customer.accounts.all()
    address_book = customer.address_book.all()

    if request.method == 'POST':
        # Update customer info
        customer_form = CustomerForm(request.POST, instance=customer)
        if customer_form.is_valid():
            customer_form.save()
            return redirect('account_settings')

        # Add new bank account
        if 'add_account' in request.POST:
            bank_account_form = BankAccountForm(request.POST)
            if bank_account_form.is_valid():
                new_account_number = bank_account_form.cleaned_data['account_number']
                if customer.accounts.filter(account_number=new_account_number).exists():
                    return render(request, 'settings.html', {'error': 'Kontoen eksisterer allerede!'})
                new_account = bank_account_form.save(commit=False)
                new_account.customer = customer
                new_account.save()
                return redirect('account_settings')

        # Add to address book
        if 'add_address_book' in request.POST:
            address_book_form = AddressBookForm(request.POST)
            if address_book_form.is_valid():
                address_book_form.save()
                return redirect('account_settings')

    else:
        customer_form = CustomerForm(instance=customer)
        bank_account_form = BankAccountForm()
        address_book_form = AddressBookForm()

    context = {
        'customer_form': customer_form,
        'bank_accounts': bank_accounts,
        'bank_account_form': bank_account_form,
        'address_book': address_book,
        'address_book_form': address_book_form,
    }
    return render(request, 'settings.html', context)

@login_required
def delete_bank_account_view(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id, customer=request.user.customer)
    account.delete()
    return redirect('account_settings')

@login_required
def delete_address_book_entry_view(request, address_book_id):
    address_book_entry = get_object_or_404(AddressBook, id=address_book_id, customer=request.user.customer)
    address_book_entry.delete()
    return redirect('account_settings')