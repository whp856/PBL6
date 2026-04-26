from django.db import models
from django.conf import settings

class Activity(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('cancelled', '已取消'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    max_participants = models.IntegerField(default=0)
    poster_url = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    activity_type = models.CharField(max_length=100, default='general')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_activities')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class ActivityRegistration(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    
    class Meta:
        unique_together = ('activity', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.activity.title}"