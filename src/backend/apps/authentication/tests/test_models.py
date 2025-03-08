"""
Unit tests for authentication models.

This module contains test cases for the Auth0User, MFAVerification, LoginAttempt,
UserSession, and RefreshToken models, verifying their functionality, methods, and
data integrity.
"""

from django.test import TestCase  # Django 4.2+
from django.utils import timezone  # Django 4.2+
from datetime import timedelta  # standard library
import uuid  # standard library

from ..models import (
    Auth0User, MFAVerification, LoginAttempt, UserSession, RefreshToken,
    MFA_METHODS, MFA_STATUS
)
from ...utils.constants import (
    MAX_LOGIN_ATTEMPTS, ACCOUNT_LOCKOUT_MINUTES,
    JWT_EXPIRATION_HOURS, REFRESH_TOKEN_EXPIRATION_DAYS
)


class Auth0UserTestCase(TestCase):
    """Test case for the Auth0User model."""

    def setUp(self):
        """Set up test data for Auth0User tests."""
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True,
            auth0_metadata='{"user_metadata": {"name": "Test User"}}',
            is_active=True
        )

    def test_auth0_user_creation(self):
        """Test that an Auth0User can be created with correct fields."""
        # Verify the user was created
        self.assertIsNotNone(self.auth0_user.id)
        
        # Verify field values
        self.assertEqual(self.auth0_user.auth0_id, 'auth0|123456789')
        self.assertEqual(self.auth0_user.email, 'test@example.com')
        self.assertEqual(self.auth0_user.email_verified, True)
        self.assertEqual(
            self.auth0_user.auth0_metadata,
            '{"user_metadata": {"name": "Test User"}}'
        )
        self.assertEqual(self.auth0_user.is_active, True)
        self.assertIsNone(self.auth0_user.last_login)
        
        # Verify string representation
        self.assertEqual(
            str(self.auth0_user),
            'test@example.com (auth0|123456789)'
        )

    def test_update_last_login(self):
        """Test the update_last_login method updates the last_login timestamp."""
        # Verify last_login is initially None
        self.assertIsNone(self.auth0_user.last_login)
        
        # Update last_login
        self.auth0_user.update_last_login()
        
        # Refresh from database
        self.auth0_user.refresh_from_db()
        
        # Verify last_login has been updated
        self.assertIsNotNone(self.auth0_user.last_login)
        
        # Verify last_login is close to current time
        self.assertLessEqual(
            self.auth0_user.last_login,
            timezone.now()
        )
        self.assertGreaterEqual(
            self.auth0_user.last_login,
            timezone.now() - timedelta(seconds=10)
        )


class MFAVerificationTestCase(TestCase):
    """Test case for the MFAVerification model."""

    def setUp(self):
        """Set up test data for MFAVerification tests."""
        # Create Auth0User for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Create MFAVerification for testing
        self.mfa = MFAVerification.objects.create(
            auth0_user=self.auth0_user,
            mfa_method=MFA_METHODS['AUTHENTICATOR'],
            verification_contact='test@example.com',
            status=MFA_STATUS['DISABLED']
        )

    def test_mfa_verification_creation(self):
        """Test that an MFAVerification can be created with correct fields."""
        # Verify the MFA verification was created
        self.assertIsNotNone(self.mfa.id)
        
        # Verify field values
        self.assertEqual(self.mfa.auth0_user, self.auth0_user)
        self.assertEqual(self.mfa.mfa_method, MFA_METHODS['AUTHENTICATOR'])
        self.assertEqual(self.mfa.verification_contact, 'test@example.com')
        self.assertEqual(self.mfa.status, MFA_STATUS['DISABLED'])
        self.assertIsNone(self.mfa.enabled_at)
        self.assertIsNone(self.mfa.last_verified_at)
        
        # Verify string representation
        self.assertEqual(
            str(self.mfa),
            f'test@example.com - {MFA_METHODS["AUTHENTICATOR"]}'
        )

    def test_is_enabled(self):
        """Test the is_enabled method returns correct status."""
        # Initially disabled
        self.assertEqual(self.mfa.status, MFA_STATUS['DISABLED'])
        self.assertFalse(self.mfa.is_enabled())
        
        # Set to enabled
        self.mfa.status = MFA_STATUS['ENABLED']
        self.mfa.save()
        self.assertTrue(self.mfa.is_enabled())
        
        # Set to pending
        self.mfa.status = MFA_STATUS['PENDING']
        self.mfa.save()
        self.assertFalse(self.mfa.is_enabled())

    def test_enable(self):
        """Test the enable method sets the correct status and timestamp."""
        # Initially disabled with no timestamp
        self.assertEqual(self.mfa.status, MFA_STATUS['DISABLED'])
        self.assertIsNone(self.mfa.enabled_at)
        
        # Enable MFA
        self.mfa.enable()
        
        # Verify status and timestamp
        self.assertEqual(self.mfa.status, MFA_STATUS['ENABLED'])
        self.assertIsNotNone(self.mfa.enabled_at)
        
        # Verify enabled_at is close to current time
        self.assertLessEqual(
            self.mfa.enabled_at,
            timezone.now()
        )
        self.assertGreaterEqual(
            self.mfa.enabled_at,
            timezone.now() - timedelta(seconds=10)
        )

    def test_disable(self):
        """Test the disable method sets the correct status."""
        # First enable to test disabling
        self.mfa.status = MFA_STATUS['ENABLED']
        self.mfa.enabled_at = timezone.now()
        self.mfa.save()
        
        # Disable MFA
        self.mfa.disable()
        
        # Verify status
        self.assertEqual(self.mfa.status, MFA_STATUS['DISABLED'])
        
        # Enabled_at should remain as it is (maintain history)
        self.assertIsNotNone(self.mfa.enabled_at)

    def test_update_verification(self):
        """Test the update_verification method updates the last_verified_at timestamp."""
        # Initially last_verified_at is None
        self.assertIsNone(self.mfa.last_verified_at)
        
        # Update verification
        self.mfa.update_verification()
        
        # Verify last_verified_at has been updated
        self.assertIsNotNone(self.mfa.last_verified_at)
        
        # Verify last_verified_at is close to current time
        self.assertLessEqual(
            self.mfa.last_verified_at,
            timezone.now()
        )
        self.assertGreaterEqual(
            self.mfa.last_verified_at,
            timezone.now() - timedelta(seconds=10)
        )


class LoginAttemptTestCase(TestCase):
    """Test case for the LoginAttempt model."""

    def setUp(self):
        """Set up test data for LoginAttempt tests."""
        self.test_email = 'test@example.com'
        self.test_ip = '192.168.1.1'
        self.test_user_agent = 'Mozilla/5.0 (Test Browser)'

    def test_login_attempt_creation(self):
        """Test that a LoginAttempt can be created with correct fields."""
        # Create a successful login attempt
        success_attempt = LoginAttempt.objects.create(
            email=self.test_email,
            success=True,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        
        # Create a failed login attempt
        failed_attempt = LoginAttempt.objects.create(
            email=self.test_email,
            success=False,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent,
            failure_reason='Invalid password'
        )
        
        # Verify attempts were created
        self.assertIsNotNone(success_attempt.id)
        self.assertIsNotNone(failed_attempt.id)
        
        # Verify field values for successful attempt
        self.assertEqual(success_attempt.email, self.test_email)
        self.assertTrue(success_attempt.success)
        self.assertEqual(success_attempt.ip_address, self.test_ip)
        self.assertEqual(success_attempt.user_agent, self.test_user_agent)
        self.assertIsNone(success_attempt.failure_reason)
        
        # Verify field values for failed attempt
        self.assertEqual(failed_attempt.email, self.test_email)
        self.assertFalse(failed_attempt.success)
        self.assertEqual(failed_attempt.ip_address, self.test_ip)
        self.assertEqual(failed_attempt.user_agent, self.test_user_agent)
        self.assertEqual(failed_attempt.failure_reason, 'Invalid password')
        
        # Verify string representation
        self.assertIn('successful login attempt', str(success_attempt))
        self.assertIn('failed login attempt', str(failed_attempt))

    def test_get_recent_failures(self):
        """Test the get_recent_failures method returns correct failed attempts."""
        # Create timestamp references
        now = timezone.now()
        one_min_ago = now - timedelta(minutes=1)
        thirty_min_ago = now - timedelta(minutes=30)
        sixty_min_ago = now - timedelta(minutes=60)
        
        # Create failed login attempts at different times
        LoginAttempt.objects.create(
            email=self.test_email,
            success=False,
            timestamp=now,
            failure_reason='Recent failure'
        )
        
        LoginAttempt.objects.create(
            email=self.test_email,
            success=False,
            timestamp=one_min_ago,
            failure_reason='Recent failure'
        )
        
        LoginAttempt.objects.create(
            email=self.test_email,
            success=False,
            timestamp=thirty_min_ago,
            failure_reason='Older failure'
        )
        
        LoginAttempt.objects.create(
            email=self.test_email,
            success=False,
            timestamp=sixty_min_ago,
            failure_reason='Old failure'
        )
        
        # Create some successful login attempts (should be excluded)
        LoginAttempt.objects.create(
            email=self.test_email,
            success=True,
            timestamp=now
        )
        
        LoginAttempt.objects.create(
            email=self.test_email,
            success=True,
            timestamp=thirty_min_ago
        )
        
        # Test with default window (ACCOUNT_LOCKOUT_MINUTES)
        recent_failures = LoginAttempt.get_recent_failures(self.test_email)
        self.assertEqual(recent_failures.count(), 3)  # 3 failures within default window
        
        # Test with custom window of 10 minutes
        recent_failures = LoginAttempt.get_recent_failures(self.test_email, minutes=10)
        self.assertEqual(recent_failures.count(), 2)  # 2 failures within 10 minutes
        
        # Test with custom window of 120 minutes
        recent_failures = LoginAttempt.get_recent_failures(self.test_email, minutes=120)
        self.assertEqual(recent_failures.count(), 4)  # All 4 failures within 120 minutes

    def test_is_account_locked(self):
        """Test the is_account_locked method correctly determines account lock status."""
        # Initially, should not be locked
        self.assertFalse(LoginAttempt.is_account_locked(self.test_email))
        
        # Create fewer than MAX_LOGIN_ATTEMPTS failed attempts
        for i in range(MAX_LOGIN_ATTEMPTS - 1):
            LoginAttempt.objects.create(
                email=self.test_email,
                success=False,
                timestamp=timezone.now() - timedelta(minutes=i),
                failure_reason=f'Failure {i+1}'
            )
        
        # Should still not be locked
        self.assertFalse(LoginAttempt.is_account_locked(self.test_email))
        
        # Add one more failed attempt to reach the limit
        LoginAttempt.objects.create(
            email=self.test_email,
            success=False,
            timestamp=timezone.now(),
            failure_reason=f'Failure {MAX_LOGIN_ATTEMPTS}'
        )
        
        # Now should be locked
        self.assertTrue(LoginAttempt.is_account_locked(self.test_email))
        
        # Create old failed attempts (outside lockout window)
        old_timestamp = timezone.now() - timedelta(minutes=ACCOUNT_LOCKOUT_MINUTES + 10)
        for i in range(MAX_LOGIN_ATTEMPTS + 2):
            LoginAttempt.objects.create(
                email='old@example.com',
                success=False,
                timestamp=old_timestamp,
                failure_reason=f'Old failure {i+1}'
            )
        
        # Old attempts should not lock the account
        self.assertFalse(LoginAttempt.is_account_locked('old@example.com'))


class UserSessionTestCase(TestCase):
    """Test case for the UserSession model."""

    def setUp(self):
        """Set up test data for UserSession tests."""
        # Create Auth0User for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Create UserSession for testing
        self.session = UserSession.objects.create(
            auth0_user=self.auth0_user,
            session_id=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(hours=JWT_EXPIRATION_HOURS),
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0 (Test Browser)'
        )

    def test_user_session_creation(self):
        """Test that a UserSession can be created with correct fields."""
        # Verify the session was created
        self.assertIsNotNone(self.session.id)
        
        # Verify field values
        self.assertEqual(self.session.auth0_user, self.auth0_user)
        self.assertIsNotNone(self.session.session_id)
        self.assertEqual(self.session.ip_address, '192.168.1.1')
        self.assertEqual(self.session.user_agent, 'Mozilla/5.0 (Test Browser)')
        self.assertTrue(self.session.is_active)
        
        # Verify created_at and last_activity are set
        self.assertIsNotNone(self.session.created_at)
        self.assertIsNotNone(self.session.last_activity)
        
        # Verify string representation
        self.assertIn('test@example.com', str(self.session))
        self.assertIn(self.session.session_id, str(self.session))

    def test_is_expired(self):
        """Test the is_expired method correctly determines session expiration."""
        # Create a session that has not expired
        future_session = UserSession.objects.create(
            auth0_user=self.auth0_user,
            session_id=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(hours=1)
        )
        
        # Create a session that has expired
        past_session = UserSession.objects.create(
            auth0_user=self.auth0_user,
            session_id=str(uuid.uuid4()),
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        # Test expiration
        self.assertFalse(future_session.is_expired())
        self.assertTrue(past_session.is_expired())

    def test_update_activity(self):
        """Test the update_activity method updates the last_activity timestamp."""
        # Store original last_activity
        original_activity = self.session.last_activity
        
        # Wait a moment to ensure time difference
        import time
        time.sleep(0.1)
        
        # Update activity
        self.session.update_activity()
        
        # Verify last_activity has been updated
        self.assertGreater(self.session.last_activity, original_activity)

    def test_extend_session(self):
        """Test the extend_session method extends the session expiration time."""
        # Store original expires_at
        original_expiry = self.session.expires_at
        
        # Extend session
        self.session.extend_session()
        
        # Verify expires_at has been extended
        self.assertGreater(self.session.expires_at, original_expiry)
        
        # Verify new expiry is close to now + JWT_EXPIRATION_HOURS
        expected_expiry = timezone.now() + timedelta(hours=JWT_EXPIRATION_HOURS)
        self.assertLessEqual(
            abs((self.session.expires_at - expected_expiry).total_seconds()),
            5  # Allow 5 seconds tolerance
        )

    def test_invalidate(self):
        """Test the invalidate method marks the session as inactive."""
        # Initially active
        self.assertTrue(self.session.is_active)
        
        # Invalidate session
        self.session.invalidate()
        
        # Verify is_active is now False
        self.assertFalse(self.session.is_active)


class RefreshTokenTestCase(TestCase):
    """Test case for the RefreshToken model."""

    def setUp(self):
        """Set up test data for RefreshToken tests."""
        # Create Auth0User for testing
        self.auth0_user = Auth0User.objects.create(
            auth0_id='auth0|123456789',
            email='test@example.com',
            email_verified=True
        )
        
        # Create RefreshToken for testing
        self.refresh_token = RefreshToken.objects.create(
            auth0_user=self.auth0_user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)
        )

    def test_refresh_token_creation(self):
        """Test that a RefreshToken can be created with correct fields."""
        # Verify the token was created
        self.assertIsNotNone(self.refresh_token.id)
        
        # Verify field values
        self.assertEqual(self.refresh_token.auth0_user, self.auth0_user)
        self.assertIsNotNone(self.refresh_token.token)
        self.assertFalse(self.refresh_token.is_revoked)
        
        # Verify created_at is set
        self.assertIsNotNone(self.refresh_token.created_at)
        
        # Verify string representation
        self.assertIn('test@example.com', str(self.refresh_token))
        self.assertIn(str(self.refresh_token.id)[:8], str(self.refresh_token))

    def test_is_valid(self):
        """Test the is_valid method correctly determines token validity."""
        # Create a token that has not expired and is not revoked
        valid_token = RefreshToken.objects.create(
            auth0_user=self.auth0_user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(days=1)
        )
        
        # Create a token that has expired
        expired_token = RefreshToken.objects.create(
            auth0_user=self.auth0_user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        # Create a token that is revoked
        revoked_token = RefreshToken.objects.create(
            auth0_user=self.auth0_user,
            token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(days=1),
            is_revoked=True
        )
        
        # Test validity
        self.assertTrue(valid_token.is_valid())
        self.assertFalse(expired_token.is_valid())
        self.assertFalse(revoked_token.is_valid())

    def test_revoke(self):
        """Test the revoke method marks the token as revoked."""
        # Initially not revoked
        self.assertFalse(self.refresh_token.is_revoked)
        self.assertTrue(self.refresh_token.is_valid())
        
        # Revoke token
        self.refresh_token.revoke()
        
        # Verify is_revoked is now True
        self.assertTrue(self.refresh_token.is_revoked)
        
        # Verify token is no longer valid
        self.assertFalse(self.refresh_token.is_valid())