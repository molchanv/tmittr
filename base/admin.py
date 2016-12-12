from django.contrib import admin
from base.models import UserProfile, Goal, Post


class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_id')

admin.site.register(UserProfile)
admin.site.register(Goal)
admin.site.register(Post)