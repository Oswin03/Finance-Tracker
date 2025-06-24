from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    is_income = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('name', 'user')
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    INCOME = 'IN'
    EXPENSE = 'EX'
    TRANSACTION_TYPES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_income = models.BooleanField(default=False)
    transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPES, default=EXPENSE)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.date}"
    
    class Meta:
        ordering = ['-date']

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    spent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def get_spent_amount(self):
        transactions = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            date__range=[self.start_date, self.end_date],
            is_income=False
        )
        return transactions.aggregate(total=Sum('amount'))['total'] or 0
    
    def get_remaining_amount(self):
        return self.amount - self.get_spent_amount()
    
    def get_percentage_spent(self):
        if self.amount == 0:
            return 0
        return min(100, (self.get_spent_amount() / self.amount) * 100)
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - ${self.amount}"
    
    class Meta:
        unique_together = ('user', 'category', 'start_date', 'end_date')

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('monthly', 'Monthly Summary'),
        ('yearly', 'Yearly Summary'),
        ('category', 'Category Breakdown'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    parameters = models.JSONField()
    file = models.FileField(upload_to='reports/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_report_type_display()}"