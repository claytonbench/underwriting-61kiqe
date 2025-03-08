from django.urls import path, include
from .views import (
    LoginView, TokenRefreshView, TokenValidateView, LogoutView,
    PasswordResetRequestView, PasswordResetConfirmView,
    MFAEnableView, MFAVerifyView, MFADisableView, MFAStatusView,
    UserProfileView, SessionListView, SessionLogoutView, SessionLogoutAllView
)

app_name = "authentication"

urlpatterns = [
    # Basic Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/validate/', TokenValidateView.as_view(), name='token-validate'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Password Management
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Multi-Factor Authentication
    path('mfa/enable/', MFAEnableView.as_view(), name='mfa-enable'),
    path('mfa/verify/', MFAVerifyView.as_view(), name='mfa-verify'),
    path('mfa/disable/', MFADisableView.as_view(), name='mfa-disable'),
    path('mfa/status/', MFAStatusView.as_view(), name='mfa-status'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    
    # Session Management
    path('sessions/', SessionListView.as_view(), name='session-list'),
    path('sessions/logout/', SessionLogoutView.as_view(), name='session-logout'),
    path('sessions/logout/all/', SessionLogoutAllView.as_view(), name='session-logout-all'),
]