from django.conf.urls import url, include

from base.views import welcome_page, goals, settings, new_goal, goal_about, new_post, delete_post, user_about, \
    first_time, success, fail, avatar_edit, avatar_delete, change_password, like, follow, bookmark, \
    subscription, feed, search, username_taken, email_taken
from loginsys.views import as_view, register, logout_view

urlpatterns = [
    url(r'^$', welcome_page, name='welcome_page'),
    url(r'^login/$', as_view, name='login'),
    url(r'^logout/&', logout_view, name='logout'),
    url(r'^register/$', register, name='register'),
#GOALS
    url(r'^(?P<username>.*)/goals/filter=(?P<filter>.*)/$', goals, name='goals'),
    url(r'^(?P<username>.*)/new-goal/$', new_goal, name='new-goal'),
    url(r'^(?P<username>.*)/goals/(?P<goal_id>.*)/$', goal_about, name='goal-about'),
    url(r'^(?P<username>.*)/(?P<goal_id>.*)/success/$', success, name='success'),
    url(r'^(?P<username>.*)/(?P<goal_id>.*)/fail/$', fail, name='fail'),
#POSTS
    url(r'^(?P<username>.*)/new-post/(?P<goal_id>.*)/$', new_post, name='new-post'),
    url(r'^(?P<username>.*)/(?P<goal_id>.*)_(?P<post_id>.*)/delete-post/$', delete_post, name='delete-post'),
#PROFILE
    url(r'^(?P<username>.*)/settings/$', settings, name='settings'),
    url(r'^(?P<username>.*)/settings/change-password/$', change_password, name='change-password'),
    url(r'^(?P<username>.*)/user-about/$', user_about, name='user-about'),
    url(r'^(?P<username>.*)/profile/$', first_time, name='first-time'),
    url(r'^(?P<username>.*)/avatar-edit/$', avatar_edit, name='avatar_edit'),
    url(r'^(?P<username>.*)/avatar-delete/$', avatar_delete, name='avatar_delete'),
    url(r'^(?P<username>.*)/subscription/$', subscription, name='subscription'),
#FEED
    url(r'^(?P<username>.*)/feed$', feed, name='feed'),
#SEARCH
    url(r'^search/', search, name='search'),
#FUNCTIONS
    url(r'^like/$', like, name='like'),
    url(r'^bookmark/$', bookmark, name='bookmark'),
    url(r'^follow/$', follow, name='follow'),
    url(r'^username_taken/$', username_taken, name='username_taken'),
    url(r'^email_taken/$', email_taken, name='email_taken'),
]
