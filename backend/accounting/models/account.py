import datetime

from django.db import models
from django.db.models import Sum
from djmoney.models.fields import MoneyField
from treenode.models import TreeNodeModel


class TransactionTypeChoices(models.TextChoices):
    INCOME = 'income', 'Income'
    EXPENSE = 'expense', 'Expense'


class AccountTypeChoices(models.TextChoices):
    ASSET = 'Asset'
    LIABILITY = 'Liability'
    EQUITY = 'Equity'
    INCOME = 'Income'
    EXPENSE = 'Expense'


class StatementChoices(models.TextChoices):
    BALANCE_SHEET = 'Balance Sheet'
    INCOME_AND_EXPENSE = 'Income and Expense'
    CASH_FLOW_STATEMENT = 'Cash Flow Statement'
    CHANGE_IN_EQUITY = 'Change in Equity'


class JournalEntryTypeChoices(models.TextChoices):
    SIMPLE_ENTRY = 'Simple Entry'
    COMPOUND_ENTRY = 'Compound Entry'
    OPENING_ENTRY = 'Opening Entry'
    TRANSFER_ENTRY = 'Transfer Entry'
    CLOSING_ENTRY = 'Closing Entry'
    ADJUSTMENT_ENTRY = 'Adjustment Entry'
    RECTIFYING_ENTRY = 'Rectifying Entry'


class Account(TreeNodeModel):
    name = models.CharField('Name', max_length=255)
    code = models.IntegerField('Code', unique=True)
    description = models.CharField('Description', max_length=150, blank=True)
    active = models.BooleanField('Active', default=True)
    type = models.CharField('Type', max_length=255, choices=AccountTypeChoices.choices)
    statement = models.CharField('Statement', max_length=255,
                                 choices=StatementChoices.choices, blank=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)
    treenode_display_field = "name"

    @property
    def acc_balance(self):
        if self.account_JE:
            return Account.objects.filter(id=self.id).aggregate(s=Sum('account_JE__debit') + Sum('account_JE__credit'))[
                's']
        else:
            return 0

    def balance(self):
        if self.type in [AccountTypeChoices.ASSET, AccountTypeChoices.LIABILITY, AccountTypeChoices.EQUITY]:
            if self.acc_balance:
                return self.acc_balance + sum(
                    [account.acc_balance for account in self.get_children() if account.acc_balance])
        else:
            return self.acc_balance


class Transaction(models.Model):
    description = models.CharField('Description', max_length=255)
    date = models.DateField('Date', default=datetime.date.today)
    type = models.CharField('Type', max_length=255, choices=TransactionTypeChoices.choices)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)


class JournalEntry(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='account_JE')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)
    debit = MoneyField(max_digits=19, decimal_places=2, null=True, blank=True)
    credit = MoneyField(max_digits=19, decimal_places=2, null=True, blank=True)
    type = models.CharField('Type', max_length=255, choices=JournalEntryTypeChoices.choices,
                            default=JournalEntryTypeChoices.SIMPLE_ENTRY)
    description = models.CharField('Description', max_length=255)
    date = models.DateField('Date', default=datetime.date.today)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        verbose_name_plural = 'Journal Entries'

    def save(self, *args, **kwargs):
        if self.debit and self.credit:
            return
        if not self.debit and not self.credit:
            return
        super(JournalEntry, self).save(*args, **kwargs)
