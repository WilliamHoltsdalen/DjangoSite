from django import forms
from .models import Customer, BankAccount, AddressBook
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2", "phone_number", "address")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

