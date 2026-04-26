from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import User
import json

# 登录页面
def user_login(request):
    return render(request, '1.html')

# 首页
def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html', {'user': request.user})
    return render(request, 'home.html')

# 注册API
@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role', 'user')

            if not username or not email or not password:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': '邮箱已被注册'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': '用户名已被使用'}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password, role=role)
            return JsonResponse({'status': 'success', 'message': '注册成功', 'user_id': user.email})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 登录API
@csrf_exempt
def user_login_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'}, status=400)

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'success', 'message': '登录成功', 'redirect_url': '/home/', 'user': {
                    'email': user.email,
                    'username': user.username,
                    'role': user.role
                }})
            else:
                return JsonResponse({'status': 'error', 'message': '邮箱或密码错误'}, status=401)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 获取个人资料API
@login_required
def get_profile(request):
    if request.method == 'GET':
        try:
            user = request.user
            return JsonResponse({'status': 'success', 'user': {
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'avatar': user.avatar.url if user.avatar else None,
                'created_at': user.created_at.isoformat()
            }})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 更新个人资料API
@login_required
@csrf_exempt
def update_profile(request):
    if request.method == 'PUT':
        try:
            user = request.user
            data = json.loads(request.body)
            username = data.get('username')
            avatar = data.get('avatar')

            if username and username != user.username:
                if User.objects.filter(username=username).exists():
                    return JsonResponse({'status': 'error', 'message': '用户名已被使用'}, status=400)
                user.username = username

            if avatar:
                pass

            user.save()
            return JsonResponse({'status': 'success', 'message': '个人资料更新成功', 'user': {
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'avatar': user.avatar.url if user.avatar else None,
                'created_at': user.created_at.isoformat()
            }})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 修改密码API
@login_required
@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        try:
            user = request.user
            data = json.loads(request.body)
            old_password = data.get('old_password')
            new_password = data.get('new_password')

            if not old_password or not new_password:
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'}, status=400)

            if not user.check_password(old_password):
                return JsonResponse({'status': 'error', 'message': '原密码错误'}, status=400)

            user.set_password(new_password)
            user.save()
            return JsonResponse({'status': 'success', 'message': '密码修改成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 重置密码API
@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'status': 'error', 'message': '缺少邮箱参数'}, status=400)

            try:
                user = User.objects.get(email=email)
                return JsonResponse({'status': 'success', 'message': '重置密码邮件已发送'})
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '邮箱不存在'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求方法'}, status=405)

# 登出API
@login_required
def user_logout(request):
    logout(request)
    return JsonResponse({'status': 'success', 'message': '登出成功'})