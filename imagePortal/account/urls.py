from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import login, logout
from django.conf import settings

urlpatterns = [
    #logowanie prze form.py
    #url(r'^login/$', views.user_login, name='login'),

    #widok logowania
    url(r'^login/$', login, name='login'),
    #widok logout, po przejsciu do logout idziemy do login.html
    url(r'^logout/$', logout, {'next_page': settings.LOGIN_REDIRECT_URL }, name='logout'),
    #url do rejestracji
    url(r'^register/$', views.register, name='register'),
    #widok main Page
    url(r'^$', views.dashboard, name='dashboard'),
    #edycja Profilu user'a
    url(r'^editProfile/$', views.editProfile, name='editProfile'),
    #lista user'ów
    url(r'^users/$', views.user_list, name='user_list'),
    #link do follows
    url(r'^users/follow/$', views.user_follow, name='user_follow'),
    #profil user'a
    url(r'^users/(?P<username>[-\w]+)/$', views.user_detail, name='user_detail'),
    #change_password
    url(r'^password/$', views.change_password,  name='change_password'),


]
