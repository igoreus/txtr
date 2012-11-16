from django.conf.urls import patterns, url
from service.views import home, login_user, logout_user, user_settings, registration, verification

urlpatterns = patterns('',
    url(r'^$', home, name="home"),
    url(r'^login/$',  login_user, name='login'),
    url(r'^logout/$',  logout_user, name='logout'),
    url(r'^settings/$',  user_settings, name='settings'),
    url(r'^registration/$', registration, name="registration"),
    url(r'^verification/(?P<key>\w*)$', verification, name="verification"),
)
