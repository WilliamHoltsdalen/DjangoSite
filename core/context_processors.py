from .models import BankAccount, Customer
from django.shortcuts import render, get_object_or_404

def account_context(request):
    account = None
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            bank_accounts = customer.accounts.all()
            account = bank_accounts.first()
        except BankAccount.DoesNotExist or Customer.DoesNotExist:
            account = None
    return {
        'account': account
    }

def customer_context(request):
    customer = None
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            customer = None
    return {'customer': customer}
