from django.contrib import admin
from django.urls import path
from Manage import views as Manage_views
from django.shortcuts import redirect
from user import views as user_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', user_views.home, name='home'),
    path('', user_views.user_login, name='user_login'),
    path('index/', Manage_views.index, name='index'),
    # 用户模块
    path('api/accounts/register/', user_views.register, name='register'),
    path('api/accounts/login/', user_views.user_login_api, name='login'),
    path('api/accounts/profile/', user_views.get_profile, name='get_profile'),
    path('api/accounts/profile/', user_views.update_profile, name='update_profile'),
    # 活动管理API模块
    path('api/activities/', Manage_views.activity_list_api, name='activity-list-api'),
    path('api/activities/create/', Manage_views.activity_create_api, name='activity-create-api'),
    path('api/activities/<int:pk>/', Manage_views.activity_detail_api, name='activity-detail-api'),
    path('api/activities/<int:pk>/edit/', Manage_views.activity_update_api, name='activity-update-api'),
    path('api/activities/<int:pk>/delete/', Manage_views.activity_delete_api, name='activity-delete-api'),
    path('api/accounts/change-password/', user_views.change_password, name='change_password'),
    path('api/accounts/reset-password/', user_views.reset_password, name='reset_password'),
    path('api/accounts/logout/', user_views.user_logout, name='logout'),
    # 活动管理模块
    path('Manage/', lambda request: redirect('activity-list')),
    path('Manage/activities/', Manage_views.ActivityListView.as_view(), name='activity-list'),
    path('Manage/activities/create/', Manage_views.activity_create, name='activity-create'),
    path('Manage/activities/<int:pk>/', Manage_views.ActivityDetailView.as_view(), name='activity-detail'),
    path('Manage/activities/<int:pk>/edit/', Manage_views.activity_edit, name='activity-edit'),
    path('Manage/activities/<int:pk>/delete/', Manage_views.activity_delete, name='activity-delete'),
    path('Manage/activities/<int:pk>/register/', Manage_views.activity_register, name='activity-register'),
    path('Manage/activities/<int:pk>/unregister/', Manage_views.activity_unregister, name='activity-unregister'),
    # 个人信息页面
    path('Manage/profile/', Manage_views.profile, name='profile'),  
]
