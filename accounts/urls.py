from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/', views.chat_view, name='chat'),
    path('verify-email/<uuid:token>/',
         views.verify_email_view, name='verify_email'),
    path('password-reset/request/', views.password_reset_request_view,
         name='password_reset_request'),
    path('password-reset/done/', views.password_reset_done_view,
         name='password_reset_done'),
    path('password-reset/<uuid:token>/',
         views.password_reset_confirm_view, name='password_reset_confirm'),
]
