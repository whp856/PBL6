from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Activity, ActivityRegistration

# Create your views here.
def index(request):
    return render(request, '1.html')

# 活动列表视图（支持按时间、类型筛选）
class ActivityListView(ListView):
    model = Activity
    template_name = 'manage/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # 按关键词搜索
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search)
            )

        # 按状态筛选
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # 按时间筛选
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_time__lte=end_date)

        # 按类型筛选
        activity_type = self.request.GET.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 预定义的活动类型列表
        predefined_types = [
            '学术讲座', '体育运动', '文艺演出', '科技创新',
            '社会实践', '志愿服务', '创业竞赛', '其他'
        ]
        # 获取数据库中已存在的活动类型
        existing_types = list(Activity.objects.values_list('activity_type', flat=True).distinct())
        # 合并预定义类型和已存在类型，去重并保持顺序
        all_types = []
        for t in predefined_types:
            if t not in all_types:
                all_types.append(t)
        for t in existing_types:
            if t and t not in all_types:
                all_types.append(t)
        context['activity_types'] = all_types
        return context

# 活动详情视图（包含报名状态）
class ActivityDetailView(DetailView):
    model = Activity
    template_name = 'manage/activity_detail.html'
    context_object_name = 'activity'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 检查当前用户是否已报名
        if self.request.user.is_authenticated:
            try:
                registration = ActivityRegistration.objects.get(activity=self.object, user=self.request.user)
                context['registration_status'] = registration.status
            except ActivityRegistration.DoesNotExist:
                context['registration_status'] = None
        else:
            context['registration_status'] = None
        # 获取活动的报名人数
        registration_count = ActivityRegistration.objects.filter(activity=self.object).count()
        context['registration_count'] = registration_count
        # 计算剩余名额
        if self.object.max_participants > 0:
            context['remaining_slots'] = self.object.max_participants - registration_count
        else:
            context['remaining_slots'] = None
        return context

# 活动发布视图（仅管理员）
@login_required
def activity_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        location = request.POST.get('location')
        max_participants = request.POST.get('max_participants', 0)
        activity_type = request.POST.get('activity_type', '其他')

        # 根据用户操作设置活动状态
        action = request.POST.get('action', 'save_draft')
        if action == 'publish':
            status = 'published'
        else:
            status = 'draft'

        # 创建活动记录
        activity = Activity.objects.create(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            max_participants=max_participants,
            status=status,
            activity_type=activity_type,
            created_by=request.user
        )

        # 如果是暂时保存，跳转到活动编辑页面
        if action == 'save_draft':
            return redirect('activity-edit', pk=activity.id)

        return redirect('activity-list')

    return render(request, 'manage/activity_form.html')

# 活动报名视图
def activity_register(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == 'POST':
        if request.user.is_authenticated:
            # 检查是否已经报名
            try:
                registration = ActivityRegistration.objects.get(activity=activity, user=request.user)
                # 已报名，更新状态
                registration.status = 'confirmed'
                registration.save()
            except ActivityRegistration.DoesNotExist:
                # 未报名，创建新报名
                ActivityRegistration.objects.create(
                    activity=activity,
                    user=request.user,
                    status='confirmed'
                )
            return redirect('activity-detail', pk=activity.id)
        else:
            # 未登录，重定向到登录页
            return redirect('login')

    return redirect('activity-detail', pk=activity.id)

# 取消报名视图
def activity_unregister(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == 'POST':
        if request.user.is_authenticated:
            # 检查是否已经报名
            try:
                registration = ActivityRegistration.objects.get(activity=activity, user=request.user)
                # 删除报名记录
                registration.delete()
            except ActivityRegistration.DoesNotExist:
                pass
            return redirect('activity-detail', pk=activity.id)
        else:
            # 未登录，重定向到登录页
            return redirect('login')

    return redirect('activity-detail', pk=activity.id)

# 活动编辑视图
@login_required
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    # 检查是否是活动创建者
    if activity.created_by != request.user:
        return redirect('activity-detail', pk=pk)

    if request.method == 'POST':
        activity.title = request.POST.get('title')
        activity.description = request.POST.get('description')
        activity.start_time = request.POST.get('start_time')
        activity.end_time = request.POST.get('end_time')
        activity.location = request.POST.get('location')
        activity.max_participants = request.POST.get('max_participants', 0)
        activity.activity_type = request.POST.get('activity_type', '其他')

        # 根据用户操作设置活动状态
        action = request.POST.get('action', 'save_draft')
        if action == 'publish':
            activity.status = 'published'
        else:
            activity.status = 'draft'

        activity.save()

        # 如果是暂时保存，停留在编辑页面
        if action == 'save_draft':
            return redirect('activity-edit', pk=pk)

        return redirect('activity-detail', pk=pk)

    return render(request, 'manage/activity_form.html', {'activity': activity})

# 活动删除视图
@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    # 检查是否是活动创建者
    if activity.created_by == request.user:
        activity.delete()

    return redirect('activity-list')

# 个人信息视图
@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        # 更新个人信息
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.avatar = request.POST.get('avatar')

        # 如果提供了新密码，则更新密码
        new_password = request.POST.get('new_password')
        if new_password:
            user.set_password(new_password)

        user.save()

        return redirect('profile')

    # 获取用户创建的活动
    user_activities = Activity.objects.filter(created_by=user)

    # 获取用户报名的活动
    user_registrations = ActivityRegistration.objects.filter(user=user)
    registered_activities = [reg.activity for reg in user_registrations]

    return render(request, 'manage/profile.html', {
        'user': user,
        'user_activities': user_activities,
        'registered_activities': registered_activities
    })

# 活动管理RESTful API

# 获取活动列表API（支持筛选和搜索）
@csrf_exempt
def activity_list_api(request):
    if request.method == 'GET':
        try:
            queryset = Activity.objects.all()

            # 按关键词搜索
            search = request.GET.get('search')
            if search:
                queryset = queryset.filter(
                    models.Q(title__icontains=search) |
                    models.Q(description__icontains=search)
                )

            # 按状态筛选
            status = request.GET.get('status')
            if status:
                queryset = queryset.filter(status=status)

            # 按时间筛选
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            if start_date:
                queryset = queryset.filter(start_time__gte=start_date)
            if end_date:
                queryset = queryset.filter(end_time__lte=end_date)

            # 按类型筛选
            activity_type = request.GET.get('activity_type')
            if activity_type:
                queryset = queryset.filter(activity_type=activity_type)

            # 序列化活动数据
            activities = []
            for activity in queryset:
                activities.append({
                    'id': activity.id,
                    'title': activity.title,
                    'description': activity.description,
                    'start_time': activity.start_time.isoformat() if activity.start_time else None,
                    'end_time': activity.end_time.isoformat() if activity.end_time else None,
                    'location': activity.location,
                    'max_participants': activity.max_participants,
                    'poster_url': activity.poster_url,
                    'status': activity.status,
                    'activity_type': activity.activity_type,
                    'creator_id': activity.created_by.id if activity.created_by else None,
                    'created_at': activity.created_at.isoformat() if activity.created_at else None
                })

            return JsonResponse({'status': 'success', 'activities': activities})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 创建活动API
@login_required
@csrf_exempt
def activity_create_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            description = data.get('description')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            location = data.get('location')
            max_participants = data.get('max_participants', 0)
            poster_url = data.get('poster_url')
            status = data.get('status', 'draft')
            activity_type = data.get('activity_type', 'general')

            if not title or not description or not start_time or not end_time or not location:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'}, status=400)

            activity = Activity.objects.create(
                title=title,
                description=description,
                start_time=start_time,
                end_time=end_time,
                location=location,
                max_participants=max_participants,
                poster_url=poster_url,
                status=status,
                activity_type=activity_type,
                created_by=request.user
            )

            return JsonResponse({
                'status': 'success',
                'message': '活动创建成功',
                'activity': {
                    'id': activity.id,
                    'title': activity.title,
                    'description': activity.description,
                    'start_time': activity.start_time.isoformat() if activity.start_time else None,
                    'end_time': activity.end_time.isoformat() if activity.end_time else None,
                    'location': activity.location,
                    'max_participants': activity.max_participants,
                    'poster_url': activity.poster_url,
                    'status': activity.status,
                    'activity_type': activity.activity_type,
                    'creator_id': activity.created_by.id if activity.created_by else None,
                    'created_at': activity.created_at.isoformat() if activity.created_at else None
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 获取活动详情API
@csrf_exempt
def activity_detail_api(request, pk):
    if request.method == 'GET':
        try:
            activity = get_object_or_404(Activity, pk=pk)

            # 序列化活动数据
            activity_data = {
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'start_time': activity.start_time.isoformat() if activity.start_time else None,
                'end_time': activity.end_time.isoformat() if activity.end_time else None,
                'location': activity.location,
                'max_participants': activity.max_participants,
                'poster_url': activity.poster_url,
                'status': activity.status,
                'activity_type': activity.activity_type,
                'creator_id': activity.created_by.id if activity.created_by else None,
                'created_at': activity.created_at.isoformat() if activity.created_at else None
            }

            return JsonResponse({'status': 'success', 'activity': activity_data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 更新活动API
@login_required
@csrf_exempt
def activity_update_api(request, pk):
    if request.method == 'PUT':
        try:
            activity = get_object_or_404(Activity, pk=pk)

            # 检查是否是活动创建者
            if activity.created_by != request.user:
                return JsonResponse({'status': 'error', 'message': '无权限修改此活动'}, status=403)

            data = json.loads(request.body)
            title = data.get('title')
            description = data.get('description')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            location = data.get('location')
            max_participants = data.get('max_participants')
            poster_url = data.get('poster_url')
            status = data.get('status')
            activity_type = data.get('activity_type')

            # 更新活动信息
            if title:
                activity.title = title
            if description:
                activity.description = description
            if start_time:
                activity.start_time = start_time
            if end_time:
                activity.end_time = end_time
            if location:
                activity.location = location
            if max_participants is not None:
                activity.max_participants = max_participants
            if poster_url:
                activity.poster_url = poster_url
            if status:
                activity.status = status
            if activity_type:
                activity.activity_type = activity_type

            activity.save()

            # 序列化更新后的活动数据
            activity_data = {
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'start_time': activity.start_time.isoformat() if activity.start_time else None,
                'end_time': activity.end_time.isoformat() if activity.end_time else None,
                'location': activity.location,
                'max_participants': activity.max_participants,
                'poster_url': activity.poster_url,
                'status': activity.status,
                'activity_type': activity.activity_type,
                'creator_id': activity.created_by.id if activity.created_by else None,
                'created_at': activity.created_at.isoformat() if activity.created_at else None
            }

            return JsonResponse({
                'status': 'success',
                'message': '活动更新成功',
                'activity': activity_data
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 删除活动API
@login_required
@csrf_exempt
def activity_delete_api(request, pk):
    if request.method == 'DELETE':
        try:
            activity = get_object_or_404(Activity, pk=pk)

            # 检查是否是活动创建者
            if activity.created_by != request.user:
                return JsonResponse({'status': 'error', 'message': '无权限删除此活动'}, status=403)

            activity.delete()
            return JsonResponse({'status': 'success', 'message': '活动删除成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)
