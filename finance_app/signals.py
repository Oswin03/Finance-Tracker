# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category

DEFAULT_CATEGORIES = [
    ('Groceries', False),
    ('Rent', False),
    ('Salary', True),
]

@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        for name, is_income in DEFAULT_CATEGORIES:
            Category.objects.create(user=instance, name=name, is_income=is_income)