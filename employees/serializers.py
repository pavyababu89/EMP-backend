from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Employee, Attendance, Leave, DailyUpdate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Department
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    user       = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model  = Employee
        fields = '__all__'


class EmployeeCreateSerializer(serializers.ModelSerializer):
    # For creating employee with username, password
    username   = serializers.CharField(write_only=True)
    password   = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name  = serializers.CharField(write_only=True)
    email      = serializers.EmailField(write_only=True)

    class Meta:
        model  = Employee
        fields = [
            'username', 'password', 'first_name', 'last_name', 'email',
            'department', 'role', 'phone', 'address', 'profile_pic'
        ]

    def create(self, validated_data):
        # Extract user fields
        username   = validated_data.pop('username')
        password   = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name  = validated_data.pop('last_name')
        email      = validated_data.pop('email')

        # Create Django User
        user = User.objects.create_user(
            username   = username,
            password   = password,
            first_name = first_name,
            last_name  = last_name,
            email      = email
        )

        # Create Employee linked to User
        employee = Employee.objects.create(user=user, **validated_data)
        return employee


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source='employee.user.get_full_name',
        read_only=True
    )

    class Meta:
        model  = Attendance
        fields = '__all__'
        read_only_fields = ['employee']  # auto set from logged in user


class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source='employee.user.get_full_name',
        read_only=True
    )

    class Meta:
        model  = Leave
        fields = '__all__'
        read_only_fields = ['employee', 'applied_on', 'reviewed_by', 'reviewed_on']


class DailyUpdateSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source='employee.user.get_full_name',
        read_only=True
    )

    class Meta:
        model  = DailyUpdate
        fields = '__all__'
        read_only_fields = ['employee', 'date', 'submitted_at']