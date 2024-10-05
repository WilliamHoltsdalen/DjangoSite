from django.contrib import admin
from.models import Customer, BankAccount, Transaction, AddressBook

# Register your models here.

admin.site.register(BankAccount)
admin.site.register(Transaction)
admin.site.register(AddressBook)


class CustomerAdmin(admin.ModelAdmin):
    model = Customer
    list_display = ('user', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'get_accounts')

    @admin.display(description='Accounts', ordering='accounts__account_number')
    def get_accounts(self, obj):
        return obj.accounts.all().count()

admin.site.register(Customer, CustomerAdmin)