import uuid
from django.db import models
# from employees.models import Employee

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    base_salary = models.IntegerField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')

    def __str__(self):
        return self.name
    
class LeaveApplication(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='leaves')
    month = models.CharField(max_length=2)  # "01".."12"
    year = models.CharField(max_length=4)   # "2025"
    leaves = models.IntegerField(default=0)

    class Meta:
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        return f"{self.employee_id} - {self.month}/{self.year} - {self.leaves}"

