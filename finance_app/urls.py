from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import add_expense, expense_list


urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='finance_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='finance_app/logout.html'), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),  # Changed name
    path('transactions/add/', views.TransactionCreateView.as_view(), name='add_transaction'),
    path('transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='edit_transaction'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='delete_transaction'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),  # Changed name
    path('categories/add/', views.CategoryCreateView.as_view(), name='add_category'),
    
    # Budgets
    path('budgets/', views.BudgetListView.as_view(), name='budget_list'),  # Changed name
    path('budgets/add/', views.BudgetCreateView.as_view(), name='add_budget'),
    path('budgets/<int:pk>/edit/', views.BudgetUpdateView.as_view(), name='edit_budget'),
    path('budgets/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='delete_budget'),
    
    # Reports
    path('reports/', views.generate_report, name='generate_report'),
    path('reports/<int:pk>/', views.view_report, name='view_report'),
    path('reports/<int:pk>/download/', views.download_report, name='download_report'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),

    path('expenses/add/', add_expense, name='add_expense'),
    path('expenses/', expense_list, name='expense_list'),


    # API
    path('api/transactions/', views.api_transactions, name='api_transactions'),
    path('api/summary/', views.api_summary, name='api_summary'),
]