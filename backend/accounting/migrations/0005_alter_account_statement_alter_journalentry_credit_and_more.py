# Generated by Django 4.1.3 on 2022-12-03 11:16

from django.db import migrations, models
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_rename_amount_journalentry_credit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='statement',
            field=models.CharField(blank=True, choices=[('balance_sheet', 'Balance Sheet'), ('income and expense', 'Income and Expense'), ('cash flow statement', 'Cash Flow Statement'), ('change in equity', 'Change in Equity')], max_length=255, verbose_name='Statement'),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='credit',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='debit',
            field=djmoney.models.fields.MoneyField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
    ]
