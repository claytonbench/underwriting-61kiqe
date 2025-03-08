from django.urls import path, include

from .views import (
    UserListCreateView,
    UserDetailView,
    BorrowerProfileView,
    SchoolAdminProfileView,
    InternalUserProfileView,
    RoleListCreateView,
    RoleDetailView,
    PermissionListCreateView,
    PermissionDetailView,
    UserRoleView,
    RolePermissionView,
    get_current_user,
    update_current_user,
    get_user_roles_view,
    get_user_permissions_view,
    change_password_view,
    reset_password_view,
)

# Define the app namespace for URL reversing
app_name = 'users'

# URL patterns for the users app
urlpatterns = [
    # User listing and creation
    path('', UserListCreateView.as_view(), name='user-list-create'),
    
    # Current user endpoints
    path('me/', get_current_user, name='current-user'),
    path('me/update/', update_current_user, name='update-current-user'),
    path('me/change-password/', change_password_view, name='change-password'),
    
    # Password reset endpoint
    path('reset-password/', reset_password_view, name='reset-password'),
    
    # User detail endpoints
    path('<uuid:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('<uuid:user_id>/roles/', get_user_roles_view, name='user-roles'),
    path('<uuid:user_id>/permissions/', get_user_permissions_view, name='user-permissions'),
    
    # User role management
    path('<uuid:user_id>/roles/<uuid:role_id>/', UserRoleView.as_view(), name='user-role-detail'),
    path('<uuid:user_id>/roles/', UserRoleView.as_view(), name='user-role-assign'),
    
    # User profile management
    path('<uuid:user_id>/borrower-profile/', BorrowerProfileView.as_view(), name='borrower-profile'),
    path('<uuid:user_id>/school-admin-profile/', SchoolAdminProfileView.as_view(), name='school-admin-profile'),
    path('<uuid:user_id>/internal-profile/', InternalUserProfileView.as_view(), name='internal-user-profile'),
    
    # Role management
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<uuid:role_id>/', RoleDetailView.as_view(), name='role-detail'),
    
    # Role permission management
    path('roles/<uuid:role_id>/permissions/', RolePermissionView.as_view(), name='role-permission-assign'),
    path('roles/<uuid:role_id>/permissions/<uuid:permission_id>/', RolePermissionView.as_view(), name='role-permission-detail'),
    
    # Permission management
    path('permissions/', PermissionListCreateView.as_view(), name='permission-list-create'),
    path('permissions/<uuid:permission_id>/', PermissionDetailView.as_view(), name='permission-detail'),
]