from .forms import CustomerForm, BankAccountForm, AddressBookForm, CustomUserCreationForm
from .models import BankAccount, Transaction, Customer, AddressBook
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.paginator import Paginator

def landing_page_view(request):
    context = {}
    return render(request, 'landing_page.html', context)

def home_view(request):
    return redirect('landing_page')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/home/')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                customer = Customer.objects.create(
                    user=user,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    phone_number=form.cleaned_data.get('phone_number', ''),
                    address=form.cleaned_data.get('address', '')
                )
                login(request, user)
                return redirect('dashboard')
            except IntegrityError:
                user.delete()
                messages.error(request, "En feil oppstod under registreringen. Vennligst prøv igjen.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return render(request, 'logout.html')

@login_required
def dashboard_view(request):
    customer = request.user.customer
    accounts = customer.accounts.all()
    transactions = Transaction.objects.filter(account__in=accounts).order_by('timestamp').reverse()[:5]
    context = {
        'transactions': transactions,
        'accounts': accounts,
    }   
    return render(request, 'dashboard.html', context)

def error_view(request):
    context={}
    return render(request, 'error.html', context)

def success_view(request):
    context={}
    return render(request, 'success.html', context)

@login_required
def deposit_view(request):
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

@login_required
def withdraw_view(request):
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

@login_required
def transfer_view(request):
    customer = request.user.customer
    accounts = customer.accounts.all()
    address_book = AddressBook.objects.filter(customer=customer)
    address_book_choices = [(entry.bank_account.account_number, f"{entry.account_holder_name} - {entry.nickname}") for entry in address_book]
    
    context = {
        'accounts': accounts,
        'receivers': address_book_choices,
    }

    if request.method == 'POST':
        amount = Decimal(request.POST['amount'])
        sender_account_id = request.POST.get('sender_account_id')
        address_book_entry_number = request.POST.get('address_book_entry_number')
        custom_receiver_number = request.POST.get('custom_account_number')

        receiver_number = custom_receiver_number if custom_receiver_number else address_book_entry_number

        sender_account = get_object_or_404(BankAccount, id=sender_account_id, customer=customer)

        receiver_account = BankAccount.objects.filter(account_number=receiver_number).first()

        if receiver_account:
            if sender_account.balance >= amount:
                sender_account.withdraw(amount)
                receiver_account.deposit(amount)

                # Sender transaction
                Transaction.objects.create(
                    account=sender_account,
                    transaction_type='transfer',
                    amount=amount,
                    balance_after=sender_account.balance,
                    receiver=receiver_account 
                )

                # Reciever transaction
                Transaction.objects.create(
                    account=receiver_account,
                    transaction_type='payment',
                    amount=amount,
                    balance_after=receiver_account.balance,
                )

                messages.success(request, 'Overføringen var vellykket!')
                return redirect('transfer')

            messages.error(request, 'Utilstrekkelige midler!')
            return redirect('transfer')

        messages.error(request, 'Mottakeren finnes ikke.')
        return redirect('transfer')

    return render(request, 'transfer.html', context)

@login_required
def check_balance_view(request):
    customer = request.user.customer
    accounts = customer.accounts.all()
    context = {
        'accounts': accounts,
    }
    return render(request, 'balance.html', context)

@login_required
def account_settings_view(request):
    customer = request.user.customer
    bank_accounts = customer.accounts.all()
    address_book = customer.address_book.all()

    if request.method == 'POST':
        # Update customer info
        if 'update_customer' in request.POST:
            customer_form = CustomerForm(request.POST, instance=customer)
            if customer_form.is_valid():
                customer_form.save()
                messages.success(request, 'Din informasjon er oppdatert')
                return redirect('account_settings')
        
        # Add new bank account
        elif 'add_account' in request.POST:
            bank_account_form = BankAccountForm(request.POST)
            if bank_account_form.is_valid():
                new_account_number = bank_account_form.cleaned_data['account_number']
                if customer.accounts.filter(account_number=new_account_number).exists():
                    messages.error(request, 'This account number already exists.')
                else:
                    new_account = bank_account_form.save(commit=False)
                    new_account.customer = customer
                    new_account.save()
                    messages.success(request, 'Ny konto lagt til')
                return redirect('account_settings')

        # Add to address book
        elif 'add_address_book' in request.POST:
            address_book_form = AddressBookForm(request.POST)
            if address_book_form.is_valid():
                new_entry = address_book_form.save(commit=False)
                new_entry.customer = customer
                new_entry.save()
                messages.success(request, 'Ny kontakt lagt til')
                return redirect('account_settings')

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
def transactions_view(request):
    customer = request.user.customer
    accounts = customer.accounts.all()
    transactions = Transaction.objects.filter(account__in=accounts).order_by('-timestamp')

    paginator = Paginator(transactions, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'transactions.html', context)

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

