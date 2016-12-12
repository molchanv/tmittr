from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse
from django.core.mail import EmailMessage
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from base.forms import GoalForm, NewPost, AvatarEdit
from base.models import UserProfile, Goal, Post
from django.utils import timezone
import datetime
from base.other_app.for_weekdays import weekdays_nums, inverse_weekdays_nums
from base.other_app.stat import stat_in_process, stat_success, stat_fail

now = timezone.now()

####################################
# GOALS
####################################

@login_required(login_url='/login/')
# страница со списком целей
def goals(request, username=None, filter=None):
    # в функцию передается username и на его основе подгружаются цели владельца username
    user = User.objects.get(username=username)
    owner = UserProfile.objects.get(user=user)
    # авторизованный пользователь
    userprofile = UserProfile.objects.get(user=request.user)
    statistics = owner.statistics.split(',')
    context = {
        'owner': owner,
        'user': user,
        'filter': filter,
        'now': now,
        'statistics': statistics,
    }

    # если авторизованный пользователь явл-ся подписчиком
    if owner.followers.filter(id=userprofile.id).exists():
        context['subscriber'] = True

    # если владельцем username оказывается авторизованный сейчас user
    if request.user == user:
        guest = False
    else:
        # если нет, то авторизованный пользователь будет гостем
        guest = True

    context['guest'] = guest

    if filter == 'all':
        # загрузить все цели
        goals = Goal.objects.filter(user=owner).order_by('-created')
        paginator = Paginator(goals, 15)
        context['goals'] = goals
    else:
        # загрузить цели со статусом status=filter
        goals = Goal.objects.filter(user=owner,status=filter).order_by('-created')
        paginator = Paginator(goals, 15)
        context['goals'] = goals

    # пагинация
    page = request.GET.get('page')
    try:
        goals_page = paginator.page(page)
    except PageNotAnInteger:
        goals_page = paginator.page(1)
    except EmptyPage:
        goals_page = paginator.page(paginator.num_pages)

    context['goals'] = goals_page

    return render(request, 'goals/goals.html', context)

@login_required(login_url='/login/')
def new_goal(request, username=None):
    user = request.user
    userprofile = UserProfile.objects.get(user=user)

    context = {
        'user': user,
        'userprofile': userprofile,
    }

    if request.method == "POST":
        # weekdays_nums - записывает в ключ "weekdays" число, несущее в себе информацио о порядковых номерах дней недели
        goal = GoalForm(weekdays_nums(request.POST))
        if goal.is_valid():
            instance = goal.save(commit=False)
            instance.user = userprofile
            instance.end = now + datetime.timedelta(days=instance.days)
            instance.save()
            # stat_in_process - изменяет статистику пользователя
            userprofile.statistics = stat_in_process(userprofile.statistics)
            userprofile.save()
            return redirect('goals', username=username, filter='all')
    else:
        return render(request, 'goals/new-goal.html', context)

@login_required(login_url='/login/')
def goal_about(request, username=None, goal_id=None):
    user = User.objects.get(username=username)
    owner = UserProfile.objects.get(user=user)
    userprofile = UserProfile.objects.get(user=request.user)
    goal = Goal.objects.get(id=goal_id)
    posts = Post.objects.filter(goal=goal).order_by('-created')
    statistics = owner.statistics.split(',')
    # inverse_weekdays_nums - преобразует число в список с днями недели
    weekdays = inverse_weekdays_nums(goal.weekdays)

    context = {
        'user': user,
        'owner': owner,
        'goal': goal,
        'posts': posts,
        'weekdays': weekdays,
        'statistics': statistics,
    }

    #
    if not goal.confirmation and now > goal.end:
        confirm = True
        context['confirm'] = confirm

    if userprofile.bookmarks.filter(id=goal.id).exists():
        context['bookmark'] = True

    if goal.likes.filter(id=request.user.id).exists():
        context['like'] = True

    if owner.followers.filter(id=userprofile.id).exists():
        context['subscriber'] = True

    if request.user == user:
        guest = False
        context['guest'] = guest
    else:
        guest = True
        context['guest'] = guest

    page = request.GET.get('page')
    paginator = Paginator(posts, 10)

    try:
        post_page = paginator.page(page)
    except PageNotAnInteger:
        post_page = paginator.page(1)
    except EmptyPage:
        post_page = paginator.page(paginator.num_pages)

    context['goals'] = post_page

    return render(request, 'goals/goal-about.html', context)

@login_required(login_url='/login/')
def success(request,goal_id=None,username=None):
    userprofile = UserProfile.objects.get(user=request.user)
    goal = Goal.objects.get(id=goal_id)

    if request.method == "POST":
        # комментарий к выполненной цели добавляется к модели Goal
        success_comment = request.POST.get('success_comment')
        goal.success_comment = success_comment
        goal.save()
        # если пользователь загрузил фото
        if request.FILES:
            success_photo = request.FILES.get('success_photo')
            # создается пост с текстом success_comment и фотографией success_photo
            Post(text=success_comment, goal=goal, image=success_photo).save()
        else:
            # создается пост с текстом success_comment
            Post(text=success_comment, goal=goal).save()

        # цель помечается как завершенная
        goal.confirmation = True
        # статус выполнено
        goal.status = 'success'
        goal.save()
        # изменяется статистика пользователя
        userprofile.statistics = stat_success(userprofile.statistics)
        userprofile.save()
        return redirect('goals', username=username,filter='all')

    return HttpResponse('not ok')

@login_required(login_url='/login/')
def fail(request,goal_id=None,username=None):
    userprofile = UserProfile.objects.get(user=request.user)
    goal = Goal.objects.get(id=goal_id)

    if request.method == "POST":
        fail_comment = request.POST.get('fail_comment')
        # комментарий к невыполненной цели добавляется к модели Goal
        goal.fail_comment = fail_comment
        goal.save()
        # создается пост с текстом fail_comment
        Post(text=fail_comment, goal=goal).save()
        goal.confirmation = True
        # статус невыполнено
        goal.status = 'failed'
        goal.save()
        # изменяется статистика пользователя
        userprofile.statistics = stat_fail(userprofile.statistics)
        userprofile.save()
        return redirect('goals', username=username,filter='all')

@login_required(login_url='/login/')
def new_post(request, username=None, goal_id=None):
    goal = Goal.objects.get(id=goal_id)
    # проверка того, что авторизованный пользователь владелец цели, для которой публикуется пост
    if goal.user.user == request.user:
        if request.method == "POST":
            post = NewPost(request.POST, request.FILES or None)
            if post.is_valid():
                instance = post.save(commit=False)
                instance.goal = goal
                instance.save()
                return redirect('goal-about', username=username,goal_id=goal_id)
            else:
                raise Http404

@login_required(login_url='/login/')
def delete_post(request, post_id=None, username=None, goal_id=None):
    instance = Post.objects.get(id=post_id)

    if instance.goal.user.user == request.user:
        instance.delete()
        return redirect('goal-about', username=username, goal_id=goal_id)
    else:
        raise Http404

####################################
# SETTINGS
####################################

@login_required(login_url='/login/')
def settings(request, username=None):
    user = request.user
    userprofile = UserProfile.objects.get(user=user)

    context = {
        'userprofile': userprofile,
    }

    if request.method == 'POST':
        data = request.POST
        # обновление данных в настройках
        user.username = data.get('username')
        user.last_name = data.get('last_name')
        user.first_name = data.get('first_name')
        user.email = data.get('email')
        userprofile.birth_year = data.get('birth_year')
        userprofile.more_info = data.get('more_info')
        userprofile.web_site = data.get('web_site')
        user.save()
        userprofile.save()

        context['success'] = 'Данные обновлены'
        return render(request, 'profile/settings.html', context)

    else:
        return render(request, 'profile/settings.html', context)

@login_required(login_url='/login/')
def change_password(request,username=None):
    user = User.objects.get(username=username)
    context = {
        'user': user,
    }
    if request.method == 'POST':
        data = request.POST
        if data['password1'] == data['password2']:
            new_password = data['password2']
            user.set_password(new_password)
            user.save()
            context['success'] = 'Пароль сохранен'
            new_user = authenticate(username=username,
                                    password=data['password1'],
                                    )
            login(request, new_user)
            return render(request, 'profile/change_password.html', context)
        else:
            context['error'] = 'Пароли не совпадают'
            return render(request, 'profile/change_password.html', context)
    else:
        return render(request, 'profile/change_password.html', context)

####################################
# WELCOME PAGE
####################################

# если пользователь заходит впервые
@login_required(login_url='/login/')
def first_time(request, username=None):
    if UserProfile.objects.filter(user=request.user):
        userprofile = UserProfile.objects.get(user=request.user)
        if userprofile.birth_year is not None:
            # если данные о пользователе заполнены, то переадресовывает в личный кабинет
            return goals(request, username=username, filter='all')
        else:
            return user_about(request, username=username)
    else:
        # пользователь заходит впервые, создается модель UserProfile
        new_userprofile = UserProfile(user=request.user)
        new_userprofile.save()
        # переадресация на страницу с заполнением информации о пользователе
        return user_about(request, username=username)

@login_required(login_url='/login/')
def user_about(request, username=None):
    # на этой странице пользователь заполняет информацию о себе
    user = request.user
    userprofile = UserProfile.objects.get(user=user)

    if request.method == 'POST':
        data = request.POST
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.email = data.get('email')
        userprofile.birth_year = data.get('birth_year')
        userprofile.avatar = 'none'
        user.save()
        userprofile.save()
        return redirect('goals', username=username, filter='all')
    else:
        return render(request, 'profile/user_about.html')

def welcome_page(request):
    user = request.user
    if user.is_authenticated():
        context = {
            'user': user,
        }
        return render(request, 'welcome-page.html', context)
    else:
        context = {
            'user': False,
        }
        return render(request, 'welcome-page.html', context)

####################################
# FEED
####################################

@login_required(login_url='/login/')
def feed(request, username=None):
    userprofile = UserProfile.objects.get(user=request.user)
    following = userprofile.following.all()
    posts = Post.objects.all().order_by('-created')
    # формирует список постов пользователей, на которых подписан авторизованный юзер
    all_posts = [post for post in posts if post.goal.user in following]
    # топ 10 целей по кол-ву лайков
    popular = Goal.objects.all().order_by('-likes_amount')[:10]
    context = {
        'userprofile': userprofile,
        'following': following,
        'all_posts': all_posts,
        'popular': popular,
    }

    paginator = Paginator(all_posts, 15)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context['all_posts'] = posts

    return render(request, 'feed/feed.html', context)

####################################
# SEARCH
####################################

@login_required(login_url='/login/')
def search(request, q=""):
    context = {}
    data = request.GET.get('q')

    # если введено меньше 3-х символов ничего не выводить
    if len(data) < 3:
        context['userprofile'] = False
        return render(request, 'search/search.html', context)
    else:
        # вывести 10 подходящих результатов
        user = User.objects.filter(username__icontains=data)[:10]
        if user:
            userprofile = UserProfile.objects.filter(user=user)
            context['userprofiles'] = userprofile
            return render(request, 'search/search.html', context)
        else:
            context['userprofile'] = False
            return render(request, 'search/search.html', context)
    
####################################
# SUBSCRIBTION
####################################

@login_required(login_url='/login/')
def subscription(request, username=None):
    # страница пописки
    user = request.user
    userprofile = UserProfile.objects.get(user=user)
    statistics = userprofile.statistics.split(',')
    bookmarks = userprofile.bookmarks.all()
    following = userprofile.following.all()
    context = {
        'owner': userprofile,
        'user': user,
        'bookmarks': bookmarks,
        'statistics': statistics,
        'following': following,
    }
    return render(request, 'profile/subscription.html', context)

####################################
# FUNCTIONS
####################################

@login_required(login_url='/login/')
def avatar_edit(request, username=None):
    userprofile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        new_avatar = AvatarEdit(request.POST, request.FILES or None, instance=userprofile)
        if new_avatar.is_valid():
            new_avatar.save()
            return redirect('goals', username=username, filter='all')

@login_required(login_url='/login/')
def avatar_delete(request, username=None):
    userprofile = UserProfile.objects.get(user=request.user)
    # если пользователь удаляет аватар, в поле avatar записывается none
    userprofile.avatar = 'none'
    userprofile.save()
    return redirect('goals', username=username, filter='all')

@login_required(login_url='/login/')
def like(request):
    if request.method == 'POST':
        goal_id = request.POST.get('goal_id')
        userprofile = UserProfile.objects.get(user=request.user)
        goal = Goal.objects.get(id=goal_id)
        # если лайк стоит - убрать
        if goal.likes.filter(id=request.user.id).exists():
            goal.likes.remove(userprofile)
            goal.likes_amount = goal.total_likes
            goal.save()
        # если лайка нет - поставить
        else:
            goal.likes.add(userprofile)
            goal.likes_amount = goal.total_likes
            goal.save()

@login_required(login_url='/login/')
def follow(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.get(username=username)
        owner = UserProfile.objects.get(user=user)
        subscriber = UserProfile.objects.get(user=request.user)
        # если subscriber подписан
        if subscriber.following.filter(id=owner.id).exists():
            subscriber.following.remove(owner)
            owner.followers.remove(subscriber)
        else:
            subscriber.following.add(owner)
            owner.followers.add(subscriber)

@login_required(login_url='/login/')
def bookmark(request):
    if request.method == 'POST':
        goal_id = request.POST.get('goal_id')
        userprofile = UserProfile.objects.get(user=request.user)
        goal = get_object_or_404(Goal, id=goal_id)

        if goal.bookmarks.filter(id=request.user.id).exists():
            goal.bookmarks.remove(userprofile)
        else:
            goal.bookmarks.add(userprofile)

def username_taken(request):
    # проверка занят ли логин
    if request.method == 'POST':
        username = request.POST.get('username')
        if User.objects.filter(username=username):
            responce = "taken"
            return HttpResponse(responce)
        else:
            responce = "ok"
            return HttpResponse(responce)

def email_taken(request):
    # проверка занят ли емайл
    if request.method == 'POST' and request.is_ajax():
        email = request.POST.get('email')
        if User.objects.filter(email=email):
            responce = 'taken'
            return HttpResponse(responce)
        else:
            responce = 'ok'
            return HttpResponse(responce)


