from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard_alias'),
    
    # Projects
    path('projects/', views.projects_list_view, name='projects'),
    path('projects/create/', views.create_project_view, name='create_project'),
    path('projects/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.edit_project_view, name='edit_project'),
    path('projects/<int:project_id>/delete/', views.delete_project_view, name='delete_project'),
    path('projects/<int:project_id>/invite/', views.invite_members_view, name='invite_members'),
    path('projects/<int:project_id>/export/', views.export_project_tasks_csv, name='export_tasks'),
    
    # Board
    path('projects/<int:project_id>/board/', views.project_board_view, name='project_board'),
    path('tasks/status/update/', views.update_task_status_api, name='update_task_status_api'),
    
    # Tasks
    path('tasks/create/<int:project_id>/', views.create_task_view, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail_view, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.edit_task_view, name='edit_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task_view, name='delete_task'),
    path('attachments/<int:attachment_id>/delete/', views.delete_attachment_view, name='delete_attachment'),
    
    # Comments
    path('comments/<int:comment_id>/edit/', views.edit_comment_view, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment_view, name='delete_comment'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Activity Log
    path('activity-logs/', views.activity_log_view, name='activity_logs'),
]
