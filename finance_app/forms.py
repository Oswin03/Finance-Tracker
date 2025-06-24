from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Transaction, Category, Budget

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'description', 'date', 'is_income']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_income']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_income': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if self.user and category and start_date and end_date:
            existing = Budget.objects.filter(
                user=self.user,
                category=category,
                start_date=start_date,
                end_date=end_date
            ).exclude(pk=self.instance.pk if self.instance.pk else None)

            if existing.exists():
                raise ValidationError("A budget already exists for this category and date range.")

        return cleaned_data

class ReportForm(forms.Form):
    REPORT_TYPES = [
        ('monthly', 'Monthly Summary'),
        ('yearly', 'Yearly Summary'),
        ('category', 'Category Breakdown'),
    ]

    report_type = forms.ChoiceField(choices=REPORT_TYPES)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    format = forms.ChoiceField(choices=[('html', 'HTML'), ('json', 'JSON'), ('csv', 'CSV')])
