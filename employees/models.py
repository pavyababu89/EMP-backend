from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ]

    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    department  = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role        = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    phone       = models.CharField(max_length=15, blank=True)
    address     = models.TextField(blank=True)
    join_date   = models.DateField(auto_now_add=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
    ]

    employee  = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date      = models.DateField()
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    check_in  = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    remarks   = models.TextField(blank=True)

    class Meta:
        unique_together = ('employee', 'date')  # one record per employee per day

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"


class Leave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('earned', 'Earned Leave'),
        ('unpaid', 'Unpaid Leave'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee    = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type  = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date  = models.DateField()
    end_date    = models.DateField()
    reason      = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_on  = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.status})"


class DailyUpdate(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
    ]

    employee     = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_updates')
    date         = models.DateField(auto_now_add=True)
    project_name = models.CharField(max_length=200)
    task_done    = models.TextField()
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.project_name} - {self.date}"