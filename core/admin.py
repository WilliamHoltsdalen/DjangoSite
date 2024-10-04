from django.contrib import admin
from.models import Customer, BankAccount, Transaction

# Register your models here.
admin.site.register(Customer)
admin.site.register(BankAccount)
admin.site.register(Transaction)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user','first_name', 'last_name', 'email', 'phone_number', 'address')
