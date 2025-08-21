# employees/serializers.py
from rest_framework import serializers
from .models import Department, Employee, LeaveApplication

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'base_salary', 'department']

class SetBaseSalarySerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    base_salary = serializers.IntegerField(min_value=0)

class LeaveUpdateSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    month = serializers.CharField(max_length=2)
    year = serializers.CharField(max_length=4)
    increment_by = serializers.IntegerField(min_value=0)

class PayableSalaryRequestSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    month = serializers.CharField(max_length=2)
    year = serializers.CharField(max_length=4)

class PayableSalaryResponseSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    month = serializers.CharField()
    year = serializers.CharField()
    base_salary = serializers.IntegerField()
    leaves = serializers.IntegerField()
    per_day = serializers.FloatField()
    deduction = serializers.FloatField()
    payable_salary = serializers.FloatField()

class HighEarnersQuerySerializer(serializers.Serializer):
    department_id = serializers.UUIDField()

class HighEarnersMonthQuerySerializer(serializers.Serializer):
    department_id = serializers.UUIDField(required=False)
    month = serializers.CharField(max_length=2)
    year = serializers.CharField(max_length=4)
