from django.urls import path
from . import views

urlpatterns = [
    path('user/login', views.login_user, name='login_user'),
    path('user/register', views.register_user, name='register_user'),
    path('user/userinfo', views.current_user, name='user_info'),
    path('user/updateMe', views.update_current_user, name='update_user_profile'),
    path('user/forgotPassword', views.user_forgot_password, name='forgot_password'),
    path('user/resetpassword', views.user_reset_password, name='reset_password'),
    path('users/', views.get_all_users, name='get_all_users'),

    path('specialist/register', views.register_specialist, name='register_specialist'),
    path('specialist/login', views.login_specialist, name='login_specialist'),
    path('specialist/userinfo', views.current_user, name='user_info'),
    path('specialists/', views.get_all_specialists, name='get_all_specialists'),
    path('specialist/updateMe', views.update_specialist_profile, name='update_specialist_profile'),
    path('specialist/forgotPassword', views.user_forgot_password, name='forgot_password'),
    path('specialist/resetPassword/<str:resetToken>', views.user_reset_password, name='reset_password'),

]
