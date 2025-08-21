from django.db.models import F, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Department, Employee, LeaveApplication
from .serializers import (
    DepartmentSerializer, EmployeeSerializer, SetBaseSalarySerializer,
    LeaveUpdateSerializer, PayableSalaryRequestSerializer, PayableSalaryResponseSerializer,
    HighEarnersQuerySerializer, HighEarnersMonthQuerySerializer
)

WORKING_DAYS_PER_MONTH = 25

class CreateDepartment(APIView):
    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateEmployee(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            # base_salary optional on creation, can be set later
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetBaseSalary(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SetBaseSalarySerializer(data=request.data)
        if serializer.is_valid():
            employee_id = serializer.validated_data['employee_id']
            base_salary = serializer.validated_data['base_salary']
            try:
                emp = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            emp.base_salary = base_salary
            emp.save()
            return Response({'message': 'Base salary updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateLeaveCount(APIView):
    """
    PATCH API to increase a leave count of employee for given month and year.
    If no record exists, it will create one and add increment_by.
    """
    def patch(self, request):
        serializer = LeaveUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        employee_id = serializer.validated_data['employee_id']
        month = serializer.validated_data['month']
        year = serializer.validated_data['year']
        inc = serializer.validated_data['increment_by']

        try:
            emp = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        leave, _ = LeaveApplication.objects.get_or_create(
            employee=emp, month=month, year=year,
            defaults={'leaves': 0}
        )
        leave.leaves = leave.leaves + inc
        leave.save()

        return Response({
            'employee_id': emp.id,
            'month': month,
            'year': year,
            'leaves': leave.leaves
        }, status=status.HTTP_200_OK)

class CalculatePayableSalary(APIView):
    """
    POST API to calculate payable salary of the given employee for given month based on the leaves:
    Payable = Base - (Leaves * (Base/25))
    """
    def post(self, request):
        req_ser = PayableSalaryRequestSerializer(data=request.data)
        if not req_ser.is_valid():
            return Response(req_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        employee_id = req_ser.validated_data['employee_id']
        month = req_ser.validated_data['month']
        year = req_ser.validated_data['year']

        try:
            emp = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        if emp.base_salary is None:
            return Response({'error': 'Base salary not set for this employee'}, status=status.HTTP_400_BAD_REQUEST)

        leave = LeaveApplication.objects.filter(employee=emp, month=month, year=year).first()
        leaves = leave.leaves if leave else 0

        base = float(emp.base_salary)
        per_day = base / WORKING_DAYS_PER_MONTH
        deduction = leaves * per_day
        payable = max(0.0, base - deduction)

        res = {
            'employee_id': emp.id,
            'month': month,
            'year': year,
            'base_salary': int(base),
            'leaves': int(leaves),
            'per_day': round(per_day, 2),
            'deduction': round(deduction, 2),
            'payable_salary': round(payable, 2)
        }
        out_ser = PayableSalaryResponseSerializer(res)
        return Response(out_ser.data, status=status.HTTP_200_OK)

class HighEarnersInDepartment(APIView):
    """
    GET API - find high earners in a department.
    A high earner has a base_salary in the top three unique base salaries of that department.
    """
    def get(self, request):
        qser = HighEarnersQuerySerializer(data=request.query_params)
        if not qser.is_valid():
            return Response(qser.errors, status=status.HTTP_400_BAD_REQUEST)

        dept_id = qser.validated_data['department_id']
        try:
            dept = Department.objects.get(id=dept_id)
        except Department.DoesNotExist:
            return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get top 3 unique base salaries in the department
        salaries = (
            Employee.objects.filter(department=dept, base_salary__isnull=False)
            .values_list('base_salary', flat=True)
            .distinct()
            .order_by('-base_salary')
        )

        top_unique = list(salaries[:3])
        # List employees whose base_salary is among top_unique
        employees = Employee.objects.filter(department=dept, base_salary__in=top_unique) \
                                    .order_by('-base_salary', 'id')

        data = [
            {
                'id': e.id,
                'name': e.name,
                'base_salary': e.base_salary,
                'department_id': str(dept.id),
                'department_name': dept.name,
            }
            for e in employees
        ]
        return Response({'top_unique_salaries': top_unique, 'employees': data}, status=status.HTTP_200_OK)

class HighEarnersInMonth(APIView):
    def get(self, request):
        qser = HighEarnersMonthQuerySerializer(data=request.query_params)
        if not qser.is_valid():
            return Response(qser.errors, status=status.HTTP_400_BAD_REQUEST)

        month = qser.validated_data['month']
        year = qser.validated_data['year']
        department_id = qser.validated_data.get('department_id')

        qs = Employee.objects.filter(base_salary__isnull=False)
        dept_name = None
        if department_id:
            try:
                dept = Department.objects.get(id=department_id)
                dept_name = dept.name
            except Department.DoesNotExist:
                return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
            qs = qs.filter(department=dept)

        # Determine top 3 unique base salaries within the (optional) department scope
        top_unique = list(
            qs.values_list('base_salary', flat=True).distinct().order_by('-base_salary')[:3]
        )

        # Collect employees matching those salaries
        employees = qs.filter(base_salary__in=top_unique).order_by('-base_salary', 'id')

        # Optionally include payable salary for the given month (for info)
        results = []
        for e in employees:
            leave = LeaveApplication.objects.filter(employee=e, month=month, year=year).first()
            leaves = leave.leaves if leave else 0
            base = float(e.base_salary)
            per_day = base / WORKING_DAYS_PER_MONTH
            deduction = leaves * per_day
            payable = max(0.0, base - deduction)

            results.append({
                'id': e.id,
                'name': e.name,
                'department_id': str(e.department_id),
                'department_name': e.department.name,
                'base_salary': int(base),
                'month': month,
                'year': year,
                'leaves': int(leaves),
                'payable_salary': round(payable, 2)
            })

        return Response({
            'top_unique_salaries': top_unique,
            'department_id': str(department_id) if department_id else None,
            'department_name': dept_name,
            'month': month,
            'year': year,
            'employees': results
        }, status=status.HTTP_200_OK)
