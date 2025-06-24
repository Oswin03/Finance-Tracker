from rest_framework import serializers
from .models import Transaction, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_income']

class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'category', 'category_id',
            'description', 'date', 'is_income'
        ]
    
    def create(self, validated_data):
        # The user is added from the request in the view
        return Transaction.objects.create(**validated_data)