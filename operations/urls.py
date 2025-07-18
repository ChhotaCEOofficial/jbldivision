from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Admin tools
    path('clear-cache/', views.clear_cache, name='clear_cache'),
    path('add-report/', views.add_report, name='add_report'),
    path('popup/close/', views.popup_close, name='popup_close'),

    # User approval
    path('users/', views.pending_users, name='pending_users'),
    path('users/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('users/reject/<int:user_id>/', views.reject_user, name='reject_user'),

    # Panels
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('data-entry/', views.data_entry, name='data_entry'),
    path('mis-reports/', views.mis_reports, name='mis_reports'),

    # Reports
    path('my-reports/', views.my_reports_view, name='my_reports'),
    path('rail-madad/', views.rail_madad_view, name='rail_madad'),
    path('jabalpur-operations/', views.jabalpur_operations_view, name='jabalpur_operations'),
    path('delete-report/<int:report_id>/', views.delete_report_view, name='delete_report'),
    path('delete-railmadad/<int:complaint_id>/', views.delete_railmadad_view, name='delete_madad'),

    
]
