from django.contrib import admin
from .models import User, Activity, ActivityRegistration

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'start_time', 'end_time', 'location', 'activity_type', 'created_by', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('title', 'location', 'description')
    ordering = ('-created_at',)

class ActivityRegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'user', 'registered_at', 'status')
    list_filter = ('status', 'registered_at')
    search_fields = ('activity__title', 'user__username')
    ordering = ('-registered_at',)

admin.site.register(User, UserAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityRegistration, ActivityRegistrationAdmin)