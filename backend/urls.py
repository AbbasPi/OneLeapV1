from django.contrib import admin
from django.urls import path

from backend.accounting.views.accounting import chart_of_accounts, journal_entry

urlpatterns = [
    path('admin/', admin.site.urls),
    path('coa/', chart_of_accounts),
    path('je/', journal_entry)
]
