"""
URL configuration for pbl6 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from pbl6.Manage import views as Manage_views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', Manage_views.index, name='index'),
    # 活动管理模块
    path('Manage/', lambda request: redirect('activity-list')),
    path('Manage/activities/', Manage_views.ActivityListView.as_view(), name='activity-list'),
    path('Manage/activities/create/', Manage_views.activity_create, name='activity-create'),
    path('Manage/activities/<int:pk>/', Manage_views.ActivityDetailView.as_view(), name='activity-detail'),
    path('Manage/activities/<int:pk>/edit/', Manage_views.activity_edit, name='activity-edit'),
    path('Manage/activities/<int:pk>/delete/', Manage_views.activity_delete, name='activity-delete'),
    path('Manage/activities/<int:pk>/register/', Manage_views.activity_register, name='activity-register'),
    # 个人信息页面
    path('Manage/profile/', Manage_views.profile, name='profile'),
]
