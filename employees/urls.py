from django.urls import path
from .views import (
    DepartmentListCreateView, DepartmentDetailView,
    EmployeeListCreateView, EmployeeDetailView, MyProfileView,
    AttendanceListView, AttendanceDetailView,
    LeaveListView, LeaveDetailView,
    DailyUpdateListView, DailyUpdateDetailView,
    api_root,
)

urlpatterns = [
    path('', api_root, name='api-root'),
    # Department URLs (Admin only)
    path('departments/', DepartmentListCreateView.as_view(), name='department-list'),
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department-detail'),

    # Employee URLs
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/me/', MyProfileView.as_view(), name='my-profile'),

    # Attendance URLs
    path('attendance/', AttendanceListView.as_view(), name='attendance-list'),
    path('attendance/<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),

    # Leave URLs
    path('leaves/', LeaveListView.as_view(), name='leave-list'),
    path('leaves/<int:pk>/', LeaveDetailView.as_view(), name='leave-detail'),

    # Daily Update URLs
    path('daily-updates/', DailyUpdateListView.as_view(), name='daily-update-list'),
    path('daily-updates/<int:pk>/', DailyUpdateDetailView.as_view(), name='daily-update-detail'),
]