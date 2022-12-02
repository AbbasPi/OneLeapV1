import datetime

from django.db import models
from django.db.models import Sum
from djmoney.models.fields import MoneyField
from treenode.models import TreeNodeModel


class TransactionTypeChoices(models.TextChoices):
    INCOME = 'income', 'Income'
    EXPENSE = 'expense', 'Expense'


class AccountTypeChoices(models.TextChoices):
    ASSET = 'asset', 'Asset'
    LIABILITY = 'liability', 'Liability'
    EQUITY = 'equity', 'Equity'
    INCOME = 'income', 'Income'
    EXPENSE = 'expense', 'Expense'


class JournalEntryTypeChoices(models.TextChoices):
    SIMPLE_ENTRY = 'SE', 'Simple Entry'
    COMPOUND_ENTRY = 'CE', 'Compound Entry'
    OPENING_ENTRY = 'OE', 'Opening Entry'
    TRANSFER_ENTRY = 'TE', 'Transfer Entry'
    CLOSING_ENTRY = 'CLE', 'Closing Entry'
    ADJUSTMENT_ENTRY = 'AE', 'Adjustment Entry'
    RECTIFYING_ENTRY = 'RE', 'Rectifying Entry'


class Account(TreeNodeModel):
    name = models.CharField('Name', max_length=255)
    code = models.IntegerField('Code', unique=True)
    description = models.CharField('Description', max_length=150, blank=True)
    active = models.BooleanField('Active', default=True)
    type = models.CharField('Type', max_length=255, choices=AccountTypeChoices.choices)
    statement = models.CharField('Statement', max_length=255,
                                 choices=[('BS', 'Balance Sheet'), ('PL', 'Profit and Loss'), ('CF', 'Cash Flow')])
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)
    treenode_display_field = "name"

    @property
    def acc_balance(self):
        return Account.objects.filter(id=self.id).aggregate(s=Sum('account_JE__debit') + Sum('account_JE__credit'))['s']

    def balance(self):
        if self.type in [AccountTypeChoices.ASSET, AccountTypeChoices.LIABILITY, AccountTypeChoices.EQUITY]:
            return self.acc_balance + sum([account.acc_balance for account in self.get_children()])
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
