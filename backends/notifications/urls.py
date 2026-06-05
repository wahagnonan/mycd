from django.urls import path

from backends.notifications.views import (
    MarkAllNotificationsReadView,
    MarkNotificationReadView,
    NotificationListView,
)

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/<int:pk>/read/", MarkNotificationReadView.as_view(), name="notification-read"),
    path("notifications/read-all/", MarkAllNotificationsReadView.as_view(), name="notification-read-all"),
]
