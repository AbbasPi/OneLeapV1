from django.shortcuts import render
from djmoney.settings import CURRENCY_CHOICES

from backend.accounting.models import Account


def chart_of_accounts(request):
    acc = Account.objects.all()
    ctx = {'accounts': acc}
    return render(request, 'accounting/chart_of_accounts.html', ctx)


def journal_entry(request):
    ctx = {'currencies': CURRENCY_CHOICES}
    return render(request, 'accounting/journal_entry.html', ctx)
