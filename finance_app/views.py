import json
from datetime import datetime, timedelta
from io import BytesIO
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.db.models import Sum, Q, F, Case, When, FloatField
from django.contrib.auth import login, logout
from django.db.models.functions import ExtractMonth, ExtractYear
from django.urls import reverse_lazy
from reportlab.pdfgen import canvas
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from .models import Transaction, Category, Budget, Report
from .forms import (
    TransactionForm, 
    CategoryForm, 
    BudgetForm, 
    ReportForm, 
    UserRegisterForm,
    UserProfileForm,
    ExpenseForm
)
from .serializers import TransactionSerializer, CategorySerializer

# ============== Authentication Views ==============
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'finance_app/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'finance_app/login.html'
    redirect_authenticated_user = True

def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.is_income = False
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'finance_app/expense_add.html', {'form': form})

def expense_list(request):
    expenses = Transaction.objects.filter(user=request.user, is_income=False).order_by('-date')
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'finance_app/expense_list.html', {
        'expenses': expenses,
        'total_expenses': total_expenses
    })

# ============== Dashboard View ==============
@login_required
def dashboard(request):
    today = datetime.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]

    transaction_expenses = Transaction.objects.filter(
        user=request.user,
        is_income=False,
        date__range=[start_of_month, end_of_month]
    ).aggregate(total=Sum('amount'))['total'] or 0

    budget_expenses = Budget.objects.filter(
        user=request.user,
        start_date__lte=end_of_month,
        end_date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_income = Transaction.objects.filter(
        user=request.user,
        is_income=True,
        date__range=[start_of_month, end_of_month]
    ).aggregate(total=Sum('amount'))['total'] or 0

    categories = Category.objects.filter(user=request.user)
    category_data = {'labels': [], 'expenses': [], 'budgets': []}

    for category in categories:
        actual_spending = Transaction.objects.filter(
            user=request.user,
            category=category,
            is_income=False,
            date__range=[start_of_month, end_of_month]
        ).aggregate(total=Sum('amount'))['total'] or 0

        budgeted_amount = Budget.objects.filter(
            user=request.user,
            category=category,
            start_date__lte=end_of_month,
            end_date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0

        if actual_spending > 0 or budgeted_amount > 0:
            category_data['labels'].append(category.name)
            category_data['expenses'].append(float(actual_spending))
            category_data['budgets'].append(float(budgeted_amount))

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'transaction_expenses': transaction_expenses,
        'budget_expenses': budget_expenses,
        'balance': total_income - transaction_expenses,
        'category_data': json.dumps(category_data),
        'current_month': start_of_month.strftime('%B %Y')
    }
    return render(request, 'finance_app/dashboard.html', context)

# ============== Transaction Views ==============
class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'finance_app/transactions/list.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance_app/transactions/add.html'
    success_url = reverse_lazy('transactions')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.user = self.request.user
        transaction.save()
        messages.success(self.request, 'Transaction added successfully!')
        return redirect(self.success_url)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance_app/transactions/edit.html'
    success_url = reverse_lazy('transactions')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.user = self.request.user
        transaction.save()
        messages.success(self.request, 'Transaction updated successfully!')
        return redirect(self.success_url)

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'finance_app/transactions/delete.html'
    success_url = reverse_lazy('transactions')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Transaction deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ============== Category Views ==============
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'finance_app/categories/list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'finance_app/categories/add.html'
    success_url = reverse_lazy('categories')

    def form_valid(self, form):
        category = form.save(commit=False)
        category.user = self.request.user
        category.save()
        messages.success(self.request, 'Category added successfully!')
        return redirect(self.success_url)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'finance_app/categories/edit.html'
    success_url = reverse_lazy('categories')

    def form_valid(self, form):
        category = form.save(commit=False)
        category.user = self.request.user
        category.save()
        messages.success(self.request, 'Category updated successfully!')
        return redirect(self.success_url)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'finance_app/categories/delete.html'
    success_url = reverse_lazy('categories')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ============== Budget Views ==============
class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'finance_app/budgets/list.html'
    context_object_name = 'budgets'
    paginate_by = 10

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category').annotate(
            progress=Case(
                When(spent__isnull=True, then=0),
                default=F('spent') / F('amount') * 100,
                output_field=FloatField()
            )
        )

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'finance_app/budgets/add.html'
    success_url = reverse_lazy('budget_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        budget = form.save(commit=False)
        budget.user = self.request.user
        budget.save()
        messages.success(self.request, 'Budget added successfully!')
        return redirect(self.success_url)

class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'finance_app/budgets/edit.html'
    success_url = reverse_lazy('budgets')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        budget = form.save(commit=False)
        budget.user = self.request.user
        budget.save()
        messages.success(self.request, 'Budget updated successfully!')
        return redirect(self.success_url)

class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = Budget
    template_name = 'finance_app/budgets/delete.html'
    success_url = reverse_lazy('budgets')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Budget deleted successfully!')
        return super().delete(request, *args, **kwargs)

# ============== Report Views ==============
@login_required
def generate_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            format = form.cleaned_data['format']

            transactions = Transaction.objects.filter(user=request.user, date__range=[start_date, end_date])

            if report_type == 'monthly':
                data = transactions.annotate(
                    month=ExtractMonth('date'),
                    year=ExtractYear('date')
                ).values('month', 'year', 'is_income').annotate(
                    total=Sum('amount')
                ).order_by('year', 'month')

                if format == 'json':
                    return JsonResponse(list(data), safe=False)
                elif format == 'csv':
                    df = pd.DataFrame(data)
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = f'attachment; filename="monthly_report_{start_date}_{end_date}.csv"'
                    df.to_csv(response, index=False)
                    return response

            return render(request, 'finance_app/reports/result.html', {
                'report_type': report_type,
                'data': data,
                'start_date': start_date,
                'end_date': end_date
            })
    else:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        form = ReportForm(initial={'start_date': start_date, 'end_date': end_date})
    return render(request, 'finance_app/reports/generate.html', {'form': form})

@login_required
def view_report(request, pk):
    report = get_object_or_404(Report, pk=pk, user=request.user)
    return render(request, 'finance_app/reports/view.html', {'report': report})

@login_required
def download_report(request, pk):
    report = get_object_or_404(Report, pk=pk, user=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{pk}.pdf"'
    p = canvas.Canvas(response)
    p.drawString(100, 100, f"Report #{report.id}")
    p.showPage()
    p.save()
    return response

# ============== API Views ==============
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_transactions(request):
    transactions = Transaction.objects.filter(user=request.user)
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_summary(request):
    summary = {
        'total_income': Transaction.objects.filter(user=request.user, is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_expenses': Transaction.objects.filter(user=request.user, is_income=False).aggregate(Sum('amount'))['amount__sum'] or 0
    }
    return Response(summary)

# ============== Profile Views ==============
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'finance_app/profile.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('login')
    return render(request, 'finance_app/delete_account.html')
