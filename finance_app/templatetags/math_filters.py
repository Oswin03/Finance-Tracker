# finance_app/templatetags/math_filters.py
from django import template

register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
    """Subtracts arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter(name='add')
def add(value, arg):
    """Adds arg to value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplies value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter(name='divide')
def divide(value, arg):
    """Divides value by arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0  # Return 0 if division fails (including division by zero)