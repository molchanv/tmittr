from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFit, ResizeToFill
now = timezone.now()

def upload_location(self,filename):
    return '%s/%s' % (self.user.id,filename)

def upload_location_for_post(self,filename):
    return '%s/%s' % (self.goal.user.id,filename)


class UserProfile(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь')
    birth_year = models.IntegerField(null=True, blank=True, verbose_name='Год рождения')
    more_info = models.TextField(max_length=140, default='', null=True, blank=True, verbose_name='Дополнительная информация')
    web_site = models.URLField(max_length=100, null=True, blank=True, default='', verbose_name='Сайт')
    avatar = ProcessedImageField(processors=[ResizeToFill(150, 150)],
                                format='JPEG', options={'quality': 70},
                                upload_to=upload_location, verbose_name='Аватар')
    # статистика (выполняется,выполнено,невыполнено)
    statistics = models.TextField(default='0,0,0', max_length=14, verbose_name='Статистика')
    followers = models.ManyToManyField('self', symmetrical=False, related_name='followers_name', blank=True, verbose_name='Подписчики')
    following = models.ManyToManyField('self', symmetrical=False, related_name='following_name', blank=True, verbose_name='Подписки')
    bookmarks = models.ManyToManyField('Goal', related_name='bookmarks', blank=True, verbose_name='Закладки')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return self.user.username


class Goal(models.Model):
    GOAL_STATUS = (
        'in-process',
        'successful',
        'failed',
    )
    title = models.CharField(max_length=75, verbose_name='Заголовок')
    description = models.TextField(max_length=300, verbose_name='Описание')
    days = models.IntegerField(verbose_name='Срок цели')
    weekdays = models.IntegerField(verbose_name='Дни отчетов')
    price_words = models.TextField(max_length=100, verbose_name='Цена слова')
    confirmation = models.BooleanField(default=False, verbose_name='Подтверждение')
    user = models.ForeignKey(UserProfile, verbose_name='Пользователь')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата начала цели')
    end = models.DateTimeField(auto_now=False, auto_now_add=False, verbose_name='Дата окончания')
    status = models.TextField(max_length=10, default=GOAL_STATUS[0], verbose_name='Статус')
    likes = models.ManyToManyField(UserProfile, related_name='likes', blank=True, verbose_name='Лайки')
    likes_amount = models.IntegerField(default=0, verbose_name='Число лайков')
    success_comment = models.TextField(max_length=400,null=True, blank=True, verbose_name='Комментарий к выполненной цели')
    fail_comment = models.TextField(max_length=400,null=True, blank=True, verbose_name='Комментарий к невыполненной цели')

    class Meta:
        verbose_name = 'Цель пользователя'
        verbose_name_plural = 'Цели пользователей'

    def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_bookmarks(self):
        return self.bookmarks.count()

    # рассчитывает процент прогресса цели для полосы прогресса
    # пока что не используется
    def goal_progress(self):
        a = self.days
        b = str(now - self.created)
        c = b.split()[0]
        if len(c) > 10:
            c = 1
            return c
        else:
            if int(c) < 0:
                return 1
            else:
                return int(int(c)/a*100)

class Post(models.Model):

    text = models.TextField(max_length=400,null=True, blank=True, verbose_name='Текст поста')
    image = ProcessedImageField(processors=[ResizeToFit(800, 600)],
                                format='JPEG', options={'quality': 70},
                                upload_to=upload_location_for_post, verbose_name='Изображения', null=True, blank=True)
    goal = models.ForeignKey(Goal, verbose_name='Цель')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Пост пользователя'
        verbose_name_plural = 'Посты пользователей'

    def __str__(self):
        return self.text



