from django import forms
from .models import Customer, BankAccount, AddressBook
from django.forms import ModelForm

# Form for updating customer info
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']

# Form for adding new bank accounts
class BankAccountForm(ModelForm):
    class Meta:
        model = BankAccount
        fields = ['account_number', 'balance']

# Form for adding to address book
class AddressBookForm(ModelForm):
    class Meta:
        model = AddressBook
        fields = ['account_holder_name', 'bank_account', 'nickname']