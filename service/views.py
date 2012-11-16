from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from service.forms import EmailAuthenticationForm, RegistrationForm
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.contrib.auth import login, logout
from django.template import RequestContext
from django.core.urlresolvers import reverse
from service.models import UserProfile


@login_required(login_url= 'login')
def home(request, **kwargs):

    context = {}
    try:
        context['user_profile'] = request.user.profile
    except UserProfile.DoesNotExist:
        context['user_profile'] = UserProfile.objects.create(user=request.user)

    return render_to_response('service/home.html', context, context_instance=RequestContext(request))

def login_user(request, **kwargs):
    next = request.POST.get('next', request.GET.get('next', reverse('home')))
    if request.method == "POST":
        form = EmailAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.user_cache
            if user and user.is_active:
                login(request, user)
            return HttpResponseRedirect(next)
    else:
        form = EmailAuthenticationForm()
    context = {
        'form': form,
        'next': next
    }
    context.update(csrf(request))
    return render_to_response("service/login.html", context, context_instance=RequestContext(request))

def logout_user (request, **kwargs):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

def user_settings(request, **kwargs):
    context = {}
    return render_to_response("service/settings.html", context, context_instance=RequestContext(request))

def registration(request, **kwargs):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.register()
            if user:
                login(request, user)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render_to_response("service/registration.html", context, context_instance=RequestContext(request))

def verification(request, **kwargs):
    if UserProfile.objects.verification(kwargs['key']):
        return HttpResponseRedirect(reverse('home'))
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')
