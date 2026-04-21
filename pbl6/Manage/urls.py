from django.urls import path
from .views import ActivityListView, ActivityDetailView, activity_create, activity_register

urlpatterns = [
    path('activities/', ActivityListView.as_view(), name='activity-list'),
    path('activities/create/', activity_create, name='activity-create'),
    path('activities/<int:pk>/', ActivityDetailView.as_view(), name='activity-detail'),
    path('activities/<int:pk>/register/', activity_register, name='activity-register'),
]