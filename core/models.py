from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, verbose_name = "Fornavn")
    last_name = models.CharField(max_length=100, verbose_name = "Etternavn")
    email =models.EmailField(verbose_name = "E-post")
    phone_number = models.CharField(max_length=20, verbose_name = "Telefonnummer")
    address = models.CharField(max_length=255, verbose_name = "Adresse")

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class BankAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=10, unique=True, verbose_name = "Kontonummer")
    balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name = "Saldo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name = "Opprettet")

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.save()
            return True
        return False

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def __str__(self):
        return f'Konto {self.account_number} - Saldo: {self.balance}'

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Innskudd'),
        ('withdraw', 'Uttak'),
        ('transfer', 'Overføring'),
        ('payment', 'Betaling'),
    ]

    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, verbose_name = "Transaksjonstype")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name = "Beløp")
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, verbose_name = "Saldo etter transaksjon")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name = "Tidspunkt")
    receiver = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='received_transactions', null=True, blank=True, verbose_name = "Mottaker")

    def __str__(self):
        return f'{self.transaction_type.capitalize()} på {self.amount} for konto {self.account.account_number}'

class AddressBook(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='address_book')
    account_holder_name = models.CharField(max_length=100, verbose_name = "Kontoeier")
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, verbose_name = "Kontonummer")
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name = "Kallenavn")

    def __str__(self):
        return f"{self.nickname or self.account_holder_name} - {self.bank_account.account_number}"