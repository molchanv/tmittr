from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.template.context_processors import csrf


#Логин
def as_view(request):
    context = {}
    context.update(csrf(request))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect ("/")

            else:
                context['error'] = 'Неверная пара логин\пароль'
                return render(request,'login.html',context)

        else:
            context['error'] = 'Ошибка. Проверьте корректность введенных данных'
            return render(request,'login.html',context)

    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def register(request):
    context = {}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)
            return HttpResponseRedirect('/', context)
        else:
            context['error'] = 'Ошибка. Проверьте корректность введенных данных'

    return render(request, 'register.html', context)