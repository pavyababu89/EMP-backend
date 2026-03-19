from django.contrib import admin
from .models import Department, Employee, Attendance, Leave, DailyUpdate


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display  = ['user', 'department', 'role', 'phone', 'join_date']
    list_filter   = ['role', 'department']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display    = ['employee', 'date', 'status', 'check_in', 'check_out']
    list_filter     = ['status', 'date']
    readonly_fields = ['employee', 'date', 'status', 'check_in', 'check_out', 'remarks']

    def has_add_permission(self, request):
        return False       # Admin CANNOT add attendance

    def has_change_permission(self, request, obj=None):
        return False       # Admin CANNOT edit attendance

    def has_delete_permission(self, request, obj=None):
        return False       # Admin CANNOT delete attendance


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display    = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter     = ['status', 'leave_type']
    readonly_fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason', 'applied_on']

    def has_add_permission(self, request):
        return False       # Admin CANNOT add leave

    def has_delete_permission(self, request, obj=None):
        return False       # Admin CANNOT delete leave


@admin.register(DailyUpdate)
class DailyUpdateAdmin(admin.ModelAdmin):
    list_display    = ['employee', 'project_name', 'status', 'date']
    list_filter     = ['status', 'date']
    readonly_fields = ['employee', 'project_name', 'task_done', 'status', 'date', 'submitted_at']

    def has_add_permission(self, request):
        return False       # Admin CANNOT add daily update

    def has_change_permission(self, request, obj=None):
        return False       # Admin CANNOT edit daily update

    def has_delete_permission(self, request, obj=None):
        return False       # Admin CANNOT delete daily update