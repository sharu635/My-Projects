from django.contrib import admin
from .models import CustomUser, Project, Task, TaskAttachment, Comment, Notification, ActivityLog

admin.site.register(CustomUser)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(TaskAttachment)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(ActivityLog)

