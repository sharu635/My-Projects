from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/project/(?P<project_id>\d+)/board/$', consumers.ProjectBoardConsumer.as_asgi()),
    re_path(r'ws/task/(?P<task_id>\d+)/comments/$', consumers.TaskCommentsConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.UserNotificationConsumer.as_asgi()),
]
