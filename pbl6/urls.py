from django.contrib import admin
from django.urls import path
from user import views as user_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', user_views.home, name='home'),
    path('', user_views.user_login, name='user_login'),
    # API路由
    path('api/accounts/register/', user_views.register, name='register'),
    path('api/accounts/login/', user_views.user_login_api, name='login'),
    path('api/accounts/profile/', user_views.get_profile, name='get_profile'),
    path('api/accounts/profile/update/', user_views.update_profile, name='update_profile'),
    path('api/accounts/change-password/', user_views.change_password, name='change_password'),
    path('api/accounts/reset-password/', user_views.reset_password, name='reset_password'),
    path('api/accounts/logout/', user_views.user_logout, name='logout'),
]