from rest_framework import serializers

from expenses.models import Expenses


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expenses
        fields = '__all__'
