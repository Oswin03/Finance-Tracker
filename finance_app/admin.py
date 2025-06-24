from django.contrib import admin
from .models import Transaction, Category, Budget, Report

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'date', 'is_income')
    list_filter = ('is_income', 'date', 'category')
    search_fields = ('description', 'user__username')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_income')
    list_filter = ('is_income',)
    search_fields = ('name', 'user__username')

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('category__name', 'user__username')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'report_type', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('user__username',)