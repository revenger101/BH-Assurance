from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    
    # Profile management
    path('profile/', views.get_user_profile, name='get_profile'),
    path('profile/update/', views.update_user_profile, name='update_profile'),
    
    # Password management
    path('change-password/', views.change_password, name='change_password'),
    path('request-password-reset/', views.request_password_reset, name='request_password_reset'),
    path('confirm-password-reset/', views.confirm_password_reset, name='confirm_password_reset'),
    
    # Session management
    path('sessions/', views.get_user_sessions, name='get_sessions'),
    path('sessions/<str:session_key>/terminate/', views.terminate_session, name='terminate_session'),
    path('sessions/terminate-all/', views.terminate_all_sessions, name='terminate_all_sessions'),
]
