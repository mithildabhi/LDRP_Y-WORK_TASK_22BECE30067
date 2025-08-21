# employees/urls.py
from django.urls import path
from .views import (
    CreateDepartment, CreateEmployee, SetBaseSalary,
    UpdateLeaveCount, CalculatePayableSalary,
    HighEarnersInDepartment, HighEarnersInMonth
)

urlpatterns = [
    path('department/', CreateDepartment.as_view(), name='create_department'),
    path('employee/', CreateEmployee.as_view(), name='create_employee'),
    path('employee/set-base-salary/', SetBaseSalary.as_view(), name='set_base_salary'),

    path('leave/update/', UpdateLeaveCount.as_view(), name='update_leave_count'),              # PATCH
    path('salary/payable/', CalculatePayableSalary.as_view(), name='calculate_payable_salary'),# POST
    path('department/high-earners/', HighEarnersInDepartment.as_view(), name='high_earners_dept'), # GET
    path('high-earners/month/', HighEarnersInMonth.as_view(), name='high_earners_month'),     # GET
]
