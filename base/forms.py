from django import forms
from django.contrib.auth.models import User
from base.models import Goal, UserProfile, Post


class GoalForm(forms.ModelForm):

        class Meta:
            model = Goal
            fields = ['title', 'description', 'days', 'weekdays', 'price_words',]

class UpdateProfile(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username',]

class UpdateUserProfile(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['birth_year', 'more_info', 'web_site',]

class NewPost(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['text','image',]

class AvatarEdit(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['avatar',]