from django.test import TestCase
from unittest.mock import MagicMock, patch
from rest_framework.test import APIRequestFactory
from rest_framework.views import View
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from core.permissions import (
    USER_ROLES, INTERNAL_ROLES,
    has_object_permission_or_403,
    IsAuthenticated, IsSystemAdmin, IsUnderwriter, IsQC,
    IsSchoolAdmin, IsBorrower, IsCoBorrower, IsInternalUser,
    ReadOnly, IsOwner, IsOwnerOrReadOnly, IsOwnerOrInternalUser,
    IsSchoolAdminForSchool, DjangoModelPermissions
)


class TestRoleBasedPermissions(TestCase):
    """Test case for role-based permission classes"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an API request factory
        self.factory = APIRequestFactory()
        
        # Create a test view
        self.view = View()
        
        # Get the User model
        User = get_user_model()
        
        # Create test users with different roles
        self.system_admin = User(username='admin', email='admin@example.com')
        self.system_admin.role = USER_ROLES['SYSTEM_ADMIN']
        
        self.underwriter = User(username='underwriter', email='underwriter@example.com')
        self.underwriter.role = USER_ROLES['UNDERWRITER']
        
        self.qc_user = User(username='qc', email='qc@example.com')
        self.qc_user.role = USER_ROLES['QC']
        
        self.school_admin = User(username='school_admin', email='school@example.com')
        self.school_admin.role = USER_ROLES['SCHOOL_ADMIN']
        
        self.borrower = User(username='borrower', email='borrower@example.com')
        self.borrower.role = USER_ROLES['BORROWER']
        
        self.co_borrower = User(username='co_borrower', email='co_borrower@example.com')
        self.co_borrower.role = USER_ROLES['CO_BORROWER']
        
        # Create test requests with different users
        self.unauthenticated_request = self.factory.get('/')
        self.unauthenticated_request.user = None
        
        self.authenticated_request = self.factory.get('/')
        self.authenticated_request.user = self.borrower
        
        self.system_admin_request = self.factory.get('/')
        self.system_admin_request.user = self.system_admin
        
        self.underwriter_request = self.factory.get('/')
        self.underwriter_request.user = self.underwriter
        
        self.qc_request = self.factory.get('/')
        self.qc_request.user = self.qc_user
        
        self.school_admin_request = self.factory.get('/')
        self.school_admin_request.user = self.school_admin
        
        self.borrower_request = self.factory.get('/')
        self.borrower_request.user = self.borrower
        
        self.co_borrower_request = self.factory.get('/')
        self.co_borrower_request.user = self.co_borrower
    
    def test_is_authenticated(self):
        """Test that IsAuthenticated permission only allows authenticated users"""
        permission = IsAuthenticated()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with authenticated request
        self.assertTrue(permission.has_permission(self.authenticated_request, self.view))
    
    def test_is_system_admin(self):
        """Test that IsSystemAdmin permission only allows system admin users"""
        permission = IsSystemAdmin()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with non-admin user
        self.assertFalse(permission.has_permission(self.borrower_request, self.view))
        
        # Test with system admin user
        self.assertTrue(permission.has_permission(self.system_admin_request, self.view))
    
    def test_is_underwriter(self):
        """Test that IsUnderwriter permission only allows underwriter users"""
        permission = IsUnderwriter()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with non-underwriter user
        self.assertFalse(permission.has_permission(self.borrower_request, self.view))
        
        # Test with underwriter user
        self.assertTrue(permission.has_permission(self.underwriter_request, self.view))
    
    def test_is_qc(self):
        """Test that IsQC permission only allows QC users"""
        permission = IsQC()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with non-QC user
        self.assertFalse(permission.has_permission(self.borrower_request, self.view))
        
        # Test with QC user
        self.assertTrue(permission.has_permission(self.qc_request, self.view))
    
    def test_is_school_admin(self):
        """Test that IsSchoolAdmin permission only allows school admin users"""
        permission = IsSchoolAdmin()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with non-school-admin user
        self.assertFalse(permission.has_permission(self.borrower_request, self.view))
        
        # Test with school admin user
        self.assertTrue(permission.has_permission(self.school_admin_request, self.view))
    
    def test_is_borrower(self):
        """Test that IsBorrower permission only allows borrower users"""
        permission = IsBorrower()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with non-borrower user
        self.assertFalse(permission.has_permission(self.school_admin_request, self.view))
        
        # Test with borrower user
        self.assertTrue(permission.has_permission(self.borrower_request, self.view))
    
    def test_is_co_borrower(self):
        """Test that IsCoBorrower permission only allows co-borrower users"""
        permission = IsCoBorrower()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with non-co-borrower user
        self.assertFalse(permission.has_permission(self.borrower_request, self.view))
        
        # Test with co-borrower user
        self.assertTrue(permission.has_permission(self.co_borrower_request, self.view))
    
    def test_is_internal_user(self):
        """Test that IsInternalUser permission only allows internal users"""
        permission = IsInternalUser()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with non-internal user (borrower, school admin)
        self.assertFalse(permission.has_permission(self.borrower_request, self.view))
        self.assertFalse(permission.has_permission(self.school_admin_request, self.view))
        
        # Test with internal users (system admin, underwriter, QC)
        self.assertTrue(permission.has_permission(self.system_admin_request, self.view))
        self.assertTrue(permission.has_permission(self.underwriter_request, self.view))
        self.assertTrue(permission.has_permission(self.qc_request, self.view))
    
    def test_read_only(self):
        """Test that ReadOnly permission only allows safe methods"""
        permission = ReadOnly()
        
        # Test with GET request (should return True)
        get_request = self.factory.get('/')
        self.assertTrue(permission.has_permission(get_request, self.view))
        
        # Test with HEAD request (should return True)
        head_request = self.factory.head('/')
        self.assertTrue(permission.has_permission(head_request, self.view))
        
        # Test with OPTIONS request (should return True)
        options_request = self.factory.options('/')
        self.assertTrue(permission.has_permission(options_request, self.view))
        
        # Test with POST request (should return False)
        post_request = self.factory.post('/')
        self.assertFalse(permission.has_permission(post_request, self.view))
        
        # Test with PUT request (should return False)
        put_request = self.factory.put('/')
        self.assertFalse(permission.has_permission(put_request, self.view))
        
        # Test with PATCH request (should return False)
        patch_request = self.factory.patch('/')
        self.assertFalse(permission.has_permission(patch_request, self.view))
        
        # Test with DELETE request (should return False)
        delete_request = self.factory.delete('/')
        self.assertFalse(permission.has_permission(delete_request, self.view))


class TestObjectLevelPermissions(TestCase):
    """Test case for object-level permission classes"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an API request factory
        self.factory = APIRequestFactory()
        
        # Create a test view
        self.view = View()
        
        # Get the User model
        User = get_user_model()
        
        # Create test users with different roles
        self.user1 = User(username='user1', email='user1@example.com')
        self.user1.role = USER_ROLES['BORROWER']
        
        self.user2 = User(username='user2', email='user2@example.com')
        self.user2.role = USER_ROLES['BORROWER']
        
        self.internal_user = User(username='internal', email='internal@example.com')
        self.internal_user.role = USER_ROLES['SYSTEM_ADMIN']
        
        self.school_admin1 = User(username='school_admin1', email='school1@example.com')
        self.school_admin1.role = USER_ROLES['SCHOOL_ADMIN']
        self.school_admin1.school_id = 1
        
        self.school_admin2 = User(username='school_admin2', email='school2@example.com')
        self.school_admin2.role = USER_ROLES['SCHOOL_ADMIN']
        self.school_admin2.school_id = 2
        
        # Create test objects with different owners
        self.obj_user1 = MagicMock()
        self.obj_user1.user = self.user1
        
        self.obj_user2 = MagicMock()
        self.obj_user2.user = self.user2
        
        self.obj_owner1 = MagicMock()
        self.obj_owner1.owner = self.user1
        
        self.obj_school1 = MagicMock()
        self.obj_school1.school_id = 1
        
        self.obj_school2 = MagicMock()
        self.obj_school2.school_id = 2
        
        self.obj_with_school = MagicMock()
        self.obj_with_school.school = MagicMock()
        self.obj_with_school.school.id = 1
        
        self.obj_with_borrower = MagicMock()
        self.obj_with_borrower.borrower = MagicMock()
        self.obj_with_borrower.borrower.school_id = 1
        
        self.obj_with_application = MagicMock()
        self.obj_with_application.application = MagicMock()
        self.obj_with_application.application.school_id = 1
        
        # Create test requests with different users and methods
        self.unauthenticated_request = self.factory.get('/')
        self.unauthenticated_request.user = None
        
        self.user1_get_request = self.factory.get('/')
        self.user1_get_request.user = self.user1
        
        self.user1_post_request = self.factory.post('/')
        self.user1_post_request.user = self.user1
        
        self.user2_get_request = self.factory.get('/')
        self.user2_get_request.user = self.user2
        
        self.user2_post_request = self.factory.post('/')
        self.user2_post_request.user = self.user2
        
        self.internal_get_request = self.factory.get('/')
        self.internal_get_request.user = self.internal_user
        
        self.internal_post_request = self.factory.post('/')
        self.internal_post_request.user = self.internal_user
        
        self.school_admin1_request = self.factory.get('/')
        self.school_admin1_request.user = self.school_admin1
        
        self.school_admin2_request = self.factory.get('/')
        self.school_admin2_request.user = self.school_admin2
    
    def test_is_owner(self):
        """Test that IsOwner permission only allows object owners"""
        permission = IsOwner()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with authenticated non-owner
        self.assertTrue(permission.has_permission(self.user1_get_request, self.view))
        self.assertFalse(permission.has_object_permission(self.user2_get_request, self.view, self.obj_user1))
        
        # Test with object owner
        self.assertTrue(permission.has_object_permission(self.user1_get_request, self.view, self.obj_user1))
        
        # Test with object that has owner attribute instead of user
        self.assertTrue(permission.has_object_permission(self.user1_get_request, self.view, self.obj_owner1))
    
    def test_is_owner_or_read_only(self):
        """Test that IsOwnerOrReadOnly allows read-only access to all, but write access only to owners"""
        permission = IsOwnerOrReadOnly()
        
        # Test with unauthenticated GET request
        self.assertTrue(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with unauthenticated POST request
        unauthenticated_post = self.factory.post('/')
        unauthenticated_post.user = None
        self.assertFalse(permission.has_permission(unauthenticated_post, self.view))
        
        # Test with authenticated non-owner GET request
        self.assertTrue(permission.has_object_permission(self.user2_get_request, self.view, self.obj_user1))
        
        # Test with authenticated non-owner POST request
        self.assertFalse(permission.has_object_permission(self.user2_post_request, self.view, self.obj_user1))
        
        # Test with object owner GET request
        self.assertTrue(permission.has_object_permission(self.user1_get_request, self.view, self.obj_user1))
        
        # Test with object owner POST request
        self.assertTrue(permission.has_object_permission(self.user1_post_request, self.view, self.obj_user1))
    
    def test_is_owner_or_internal_user(self):
        """Test that IsOwnerOrInternalUser allows access to object owners or internal users"""
        permission = IsOwnerOrInternalUser()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with authenticated non-owner, non-internal user
        self.assertTrue(permission.has_permission(self.user2_get_request, self.view))
        self.assertFalse(permission.has_object_permission(self.user2_get_request, self.view, self.obj_user1))
        
        # Test with object owner
        self.assertTrue(permission.has_object_permission(self.user1_get_request, self.view, self.obj_user1))
        
        # Test with internal user (system admin, underwriter, QC)
        self.assertTrue(permission.has_object_permission(self.internal_get_request, self.view, self.obj_user1))
    
    def test_is_school_admin_for_school(self):
        """Test that IsSchoolAdminForSchool allows school admins to access their school's data"""
        permission = IsSchoolAdminForSchool()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with non-school-admin user
        self.assertFalse(permission.has_permission(self.user1_get_request, self.view))
        
        # Test with school admin for different school
        self.assertTrue(permission.has_permission(self.school_admin2_request, self.view))
        self.assertFalse(permission.has_object_permission(self.school_admin2_request, self.view, self.obj_school1))
        
        # Test with school admin for the object's school
        self.assertTrue(permission.has_object_permission(self.school_admin1_request, self.view, self.obj_school1))
        
        # Test different object structures (school direct, through relationship, etc)
        self.assertTrue(permission.has_object_permission(self.school_admin1_request, self.view, self.obj_with_school))
        self.assertTrue(permission.has_object_permission(self.school_admin1_request, self.view, self.obj_with_borrower))
        self.assertTrue(permission.has_object_permission(self.school_admin1_request, self.view, self.obj_with_application))


class TestDjangoModelPermissions(TestCase):
    """Test case for DjangoModelPermissions class"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an API request factory
        self.factory = APIRequestFactory()
        
        # Create a test view with a queryset
        self.view = MagicMock()
        self.view.queryset = MagicMock()
        self.view.queryset.model = MagicMock()
        self.view.queryset.model._meta = MagicMock()
        self.view.queryset.model._meta.app_label = 'testapp'
        self.view.queryset.model._meta.model_name = 'testmodel'
        
        # Get the User model
        User = get_user_model()
        
        # Create test users with different permissions
        self.user_no_perms = User(username='no_perms', email='no_perms@example.com')
        self.user_no_perms.is_authenticated = True
        self.user_no_perms.is_superuser = False
        self.user_no_perms.has_perms = MagicMock(return_value=False)
        
        self.user_with_view_perm = User(username='view_perm', email='view_perm@example.com')
        self.user_with_view_perm.is_authenticated = True
        self.user_with_view_perm.is_superuser = False
        
        # Define has_perms behavior based on input
        def has_perms_view(perms):
            return len(perms) == 1 and perms[0] == 'testapp.view_testmodel'
            
        self.user_with_view_perm.has_perms = MagicMock(side_effect=has_perms_view)
        
        self.user_with_add_perm = User(username='add_perm', email='add_perm@example.com')
        self.user_with_add_perm.is_authenticated = True
        self.user_with_add_perm.is_superuser = False
        
        def has_perms_add(perms):
            return len(perms) == 1 and perms[0] == 'testapp.add_testmodel'
            
        self.user_with_add_perm.has_perms = MagicMock(side_effect=has_perms_add)
        
        self.user_with_change_perm = User(username='change_perm', email='change_perm@example.com')
        self.user_with_change_perm.is_authenticated = True
        self.user_with_change_perm.is_superuser = False
        
        def has_perms_change(perms):
            return len(perms) == 1 and perms[0] == 'testapp.change_testmodel'
            
        self.user_with_change_perm.has_perms = MagicMock(side_effect=has_perms_change)
        
        self.user_with_delete_perm = User(username='delete_perm', email='delete_perm@example.com')
        self.user_with_delete_perm.is_authenticated = True
        self.user_with_delete_perm.is_superuser = False
        
        def has_perms_delete(perms):
            return len(perms) == 1 and perms[0] == 'testapp.delete_testmodel'
            
        self.user_with_delete_perm.has_perms = MagicMock(side_effect=has_perms_delete)
        
        # Create test requests with different users and methods
        self.unauthenticated_request = self.factory.get('/')
        self.unauthenticated_request.user = None
        
        self.get_request_no_perms = self.factory.get('/')
        self.get_request_no_perms.user = self.user_no_perms
        
        self.get_request_view_perm = self.factory.get('/')
        self.get_request_view_perm.user = self.user_with_view_perm
        
        self.post_request_no_perms = self.factory.post('/')
        self.post_request_no_perms.user = self.user_no_perms
        
        self.post_request_add_perm = self.factory.post('/')
        self.post_request_add_perm.user = self.user_with_add_perm
        
        self.put_request_no_perms = self.factory.put('/')
        self.put_request_no_perms.user = self.user_no_perms
        
        self.put_request_change_perm = self.factory.put('/')
        self.put_request_change_perm.user = self.user_with_change_perm
        
        self.delete_request_no_perms = self.factory.delete('/')
        self.delete_request_no_perms.user = self.user_no_perms
        
        self.delete_request_delete_perm = self.factory.delete('/')
        self.delete_request_delete_perm.user = self.user_with_delete_perm
    
    def test_has_permission(self):
        """Test that DjangoModelPermissions checks for appropriate model permissions"""
        permission = DjangoModelPermissions()
        
        # Test with unauthenticated request
        self.assertFalse(permission.has_permission(self.unauthenticated_request, self.view))
        
        # Test with authenticated user without permissions
        self.assertFalse(permission.has_permission(self.post_request_no_perms, self.view))
        
        # Test with user having view permission
        self.assertTrue(permission.has_permission(self.get_request_view_perm, self.view))
        
        # Test with user having add permission
        self.assertTrue(permission.has_permission(self.post_request_add_perm, self.view))
        
        # Test with user having change permission
        self.assertTrue(permission.has_permission(self.put_request_change_perm, self.view))
        
        # Test with user having delete permission
        self.assertTrue(permission.has_permission(self.delete_request_delete_perm, self.view))
    
    def test_perms_map(self):
        """Test that perms_map correctly maps HTTP methods to required permissions"""
        permission = DjangoModelPermissions()
        
        # Assert that GET maps to view permission
        self.assertEqual(permission.perms_map['GET'], ['%(app_label)s.view_%(model_name)s'])
        
        # Assert that POST maps to add permission
        self.assertEqual(permission.perms_map['POST'], ['%(app_label)s.add_%(model_name)s'])
        
        # Assert that PUT/PATCH maps to change permission
        self.assertEqual(permission.perms_map['PUT'], ['%(app_label)s.change_%(model_name)s'])
        self.assertEqual(permission.perms_map['PATCH'], ['%(app_label)s.change_%(model_name)s'])
        
        # Assert that DELETE maps to delete permission
        self.assertEqual(permission.perms_map['DELETE'], ['%(app_label)s.delete_%(model_name)s'])


class TestUtilityFunctions(TestCase):
    """Test case for permission utility functions"""
    
    def setUp(self):
        """Set up test data before each test method runs"""
        # Create an API request factory
        self.factory = APIRequestFactory()
        
        # Create a test view
        self.view = View()
        
        # Get the User model
        User = get_user_model()
        
        # Create test users
        self.user = User(username='test', email='test@example.com')
        
        # Create test objects
        self.obj = MagicMock()
        
        # Create test requests
        self.request = self.factory.get('/')
        self.request.user = self.user
    
    def test_has_object_permission_or_403(self):
        """Test that has_object_permission_or_403 raises PermissionDenied when permission is denied"""
        # Create a mock permission class that returns True
        permission_allow = MagicMock()
        permission_allow.has_object_permission = MagicMock(return_value=True)
        
        # Call has_object_permission_or_403 with this permission (should return True)
        result = has_object_permission_or_403(permission_allow, self.request, self.view, self.obj)
        self.assertTrue(result)
        
        # Create a mock permission class that returns False
        permission_deny = MagicMock()
        permission_deny.has_object_permission = MagicMock(return_value=False)
        
        # Call has_object_permission_or_403 with this permission (should raise PermissionDenied)
        with self.assertRaises(PermissionDenied):
            has_object_permission_or_403(permission_deny, self.request, self.view, self.obj)
            
        # Create a mock permission class without has_object_permission method
        permission_no_method = MagicMock(spec=[])
        
        # Call with permission that doesn't have has_object_permission (should return True)
        result = has_object_permission_or_403(permission_no_method, self.request, self.view, self.obj)
        self.assertTrue(result)