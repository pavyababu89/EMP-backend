from rest_framework import status
from rest_framework.views import APIView          # ← correct
from rest_framework.response import Response
from rest_framework.decorators import api_view    # ← ADD this
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Department, Employee, Attendance, Leave, DailyUpdate
from .serializers import (
    DepartmentSerializer, EmployeeSerializer, EmployeeCreateSerializer,
    AttendanceSerializer, LeaveSerializer, DailyUpdateSerializer
)
from .permissions import IsAdmin, IsEmployee, IsAdminOrEmployee, IsAdminReadOnlyOrEmployee


# ─── DEPARTMENT VIEWS ─────────────────────────────────────────────────────────

class DepartmentListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        departments = Department.objects.all()
        serializer  = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartmentDetailView(APIView):
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        try:
            return Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return None

    def get(self, request, pk):
        dept = self.get_object(pk)
        if not dept:
            return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DepartmentSerializer(dept).data)

    def put(self, request, pk):
        dept = self.get_object(pk)
        if not dept:
            return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = DepartmentSerializer(dept, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        dept = self.get_object(pk)
        if not dept:
            return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
        dept.delete()
        return Response({'message': 'Department deleted'}, status=status.HTTP_204_NO_CONTENT)


# ─── EMPLOYEE VIEWS ───────────────────────────────────────────────────────────

class EmployeeListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAdmin()]
        return [IsAdmin()]

    def get(self, request):
        employees  = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailView(APIView):

    def get_object(self, pk):
        try:
            return Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return None

    def get_permissions(self):
        return [IsAdminOrEmployee()]

    def get(self, request, pk):
        emp = self.get_object(pk)
        if not emp:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        # Employee can only view their own profile
        if request.user.employee.role == 'employee' and emp.user != request.user:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        return Response(EmployeeSerializer(emp).data)

    def put(self, request, pk):
        if request.user.employee.role != 'admin':
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        emp = self.get_object(pk)
        if not emp:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update User fields
        user = emp.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name  = request.data.get('last_name', user.last_name)
        user.email      = request.data.get('email', user.email)
        if request.data.get('password'):
            user.set_password(request.data.get('password'))
        user.save()

        # Update Employee fields
        emp.phone   = request.data.get('phone', emp.phone)
        emp.address = request.data.get('address', emp.address)
        emp.role    = request.data.get('role', emp.role)
        if request.data.get('department'):
            try:
                emp.department = Department.objects.get(pk=request.data.get('department'))
            except Department.DoesNotExist:
                pass
        emp.save()

        return Response(EmployeeSerializer(emp).data)
        
    def delete(self, request, pk):
        if request.user.employee.role != 'admin':
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        emp = self.get_object(pk)
        if not emp:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        emp.user.delete()  # deletes user and employee both
        return Response({'message': 'Employee deleted'}, status=status.HTTP_204_NO_CONTENT)


class MyProfileView(APIView):
    """Employee can view their own profile"""
    permission_classes = [IsAdminOrEmployee]

    def get(self, request):
        emp = request.user.employee
        return Response(EmployeeSerializer(emp).data)


# ─── ATTENDANCE VIEWS ─────────────────────────────────────────────────────────

class AttendanceListView(APIView):
    """
    Admin  → GET all attendance records (no edit)
    Employee → GET own records + POST mark attendance
    """
    permission_classes = [IsAdminReadOnlyOrEmployee]

    def get(self, request):
        if request.user.employee.role == 'admin':
            attendance = Attendance.objects.all().order_by('-date')
        else:
            attendance = Attendance.objects.filter(
                employee=request.user.employee
            ).order_by('-date')
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Only employee can mark attendance
        if request.user.employee.role == 'admin':
            return Response({'error': 'Admin cannot mark attendance'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=request.user.employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceDetailView(APIView):
    """Employee can edit own attendance. Admin cannot edit."""
    permission_classes = [IsAdminReadOnlyOrEmployee]

    def get_object(self, pk):
        try:
            return Attendance.objects.get(pk=pk)
        except Attendance.DoesNotExist:
            return None

    def get(self, request, pk):
        att = self.get_object(pk)
        if not att:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AttendanceSerializer(att).data)

    def put(self, request, pk):
        if request.user.employee.role == 'admin':
            return Response({'error': 'Admin cannot edit attendance'}, status=status.HTTP_403_FORBIDDEN)
        att = self.get_object(pk)
        if not att:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        if att.employee != request.user.employee:
            return Response({'error': 'You can only edit your own attendance'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AttendanceSerializer(att, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── LEAVE VIEWS ──────────────────────────────────────────────────────────────

class LeaveListView(APIView):
    """
    Admin    → GET all leaves
    Employee → GET own leaves + POST apply leave
    """
    permission_classes = [IsAdminOrEmployee]

    def get(self, request):
        if request.user.employee.role == 'admin':
            leaves = Leave.objects.all().order_by('-applied_on')
        else:
            leaves = Leave.objects.filter(
                employee=request.user.employee
            ).order_by('-applied_on')
        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.employee.role == 'admin':
            return Response({'error': 'Admin cannot apply for leave'}, status=status.HTTP_403_FORBIDDEN)
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=request.user.employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveDetailView(APIView):
    """Admin can only approve/reject. Employee can view own."""
    permission_classes = [IsAdminOrEmployee]

    def get_object(self, pk):
        try:
            return Leave.objects.get(pk=pk)
        except Leave.DoesNotExist:
            return None

    def get(self, request, pk):
        leave = self.get_object(pk)
        if not leave:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.employee.role == 'employee' and leave.employee != request.user.employee:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        return Response(LeaveSerializer(leave).data)

    def patch(self, request, pk):
        """Admin approves or rejects leave"""
        if request.user.employee.role != 'admin':
            return Response({'error': 'Only admin can approve/reject leave'}, status=status.HTTP_403_FORBIDDEN)
        leave = self.get_object(pk)
        if not leave:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('status')
        if new_status not in ['approved', 'rejected']:
            return Response({'error': 'Status must be approved or rejected'}, status=status.HTTP_400_BAD_REQUEST)
        leave.status      = new_status
        leave.reviewed_by = request.user
        leave.reviewed_on = timezone.now()
        leave.save()
        return Response(LeaveSerializer(leave).data)


# ─── DAILY UPDATE VIEWS ───────────────────────────────────────────────────────

class DailyUpdateListView(APIView):
    """
    Admin    → GET all daily updates (no edit)
    Employee → GET own + POST submit update
    """
    permission_classes = [IsAdminReadOnlyOrEmployee]

    def get(self, request):
        if request.user.employee.role == 'admin':
            updates = DailyUpdate.objects.all().order_by('-submitted_at')
        else:
            updates = DailyUpdate.objects.filter(
                employee=request.user.employee
            ).order_by('-submitted_at')
        serializer = DailyUpdateSerializer(updates, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.employee.role == 'admin':
            return Response({'error': 'Admin cannot submit daily updates'}, status=status.HTTP_403_FORBIDDEN)
        serializer = DailyUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(employee=request.user.employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DailyUpdateDetailView(APIView):
    """Admin can only view. Employee can view own."""
    permission_classes = [IsAdminReadOnlyOrEmployee]

    def get_object(self, pk):
        try:
            return DailyUpdate.objects.get(pk=pk)
        except DailyUpdate.DoesNotExist:
            return None

    def get(self, request, pk):
        update = self.get_object(pk)
        if not update:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.employee.role == 'employee' and update.employee != request.user.employee:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        return Response(DailyUpdateSerializer(update).data)

@api_view(['GET'])
def api_root(request):
    return Response({
        'departments':   'http://127.0.0.1:8000/api/departments/',
        'employees':     'http://127.0.0.1:8000/api/employees/',
        'attendance':    'http://127.0.0.1:8000/api/attendance/',
        'leaves':        'http://127.0.0.1:8000/api/leaves/',
        'daily_updates': 'http://127.0.0.1:8000/api/daily-updates/',
    })