from authservice.models import User, TokenManager, TokenType
from datetime import timedelta
from django.test import TestCase
from scalamed.logging import log
from unittest import mock


class UserTestCase(TestCase):
    def setUp(self):
        log.setLevel(100)

        self.alice = User.objects.create_user(
            username=None,
            email="alice@example.com",
            password="correcthorsebatterystaple")

        self.bob = User.objects.create_user(
            username=None,
            email="bob@example.com",
            password="password123")

    def tearDown(self):
        log.setLevel(30)

    def test_create_user(self):
        """Test create_user creates a user with working defaults."""

        user = self.bob
        self.assertFalse(hasattr(user, 'username'))
        self.assertEqual(user.email, "bob@example.com")
        self.assertNotEqual(user.password, "password123")
        self.assertIsNotNone(user.uuid)
        self.assertEqual(len(user.uuid), 36)
        self.assertEqual(user.role, User.Role.PATIENT)

    def test_counter(self):
        user = self.bob
        self.assertEquals(user.counter(), 0)
        self.assertEquals(user.counter(), 1)
        self.assertEquals(user.counter(), 2)
        self.assertEquals(user.counter(), 3)

    def test_privatekey_basic(self):
        self.assertEquals(self.alice.private_key(), self.alice.private_key())
        self.assertNotEqual(self.alice.private_key(), self.bob.private_key())

    def test_nonce_basic(self):
        nonces = set()
        for i in range(0, 1000):
            nonce = self.bob.nonce()
            self.assertFalse(nonce in nonces)
            nonces.add(nonce)

    def test_TokenManager_generate(self):
        """Test the generation and validation of tokens"""
        user = self.bob
        for kind in list(TokenType):
            token = TokenManager.generate(user, kind)
            self.assertTrue(TokenManager.validate(user, token, kind))

    @mock.patch('authservice.models.TokenType.ttl')
    def test_TokenManager_token_expires(self, mock_TokenType):

        def instantly_expire():
            return timedelta(seconds=-1)

        mock_TokenType.side_effect = instantly_expire

        user = self.bob
        token = TokenManager.generate(user, TokenType.LEVEL_ZERO)
        claims = TokenManager.validate(user, token, TokenType.LEVEL_ZERO)
        self.assertFalse(claims)

    def test_TokenManager_generate_weird_kind(self):

        with self.assertRaises(ValueError):
            TokenManager.generate(self.bob, TokenType(400))

        with self.assertRaises(Exception):
            TokenManager.generate(self.bob, 400)

    def test_TokenManager_deletes(self):
        token = TokenManager.generate(self.bob, TokenType.LEVEL_ZERO)
        claims = TokenManager.validate(self.bob, token, TokenType.LEVEL_ZERO)
        self.assertTrue(TokenManager.delete(self.bob, claims))
        self.assertFalse(
            TokenManager.validate(self.bob, token, TokenType.LEVEL_ZERO))

    def test_TokenManager_validate_twice(self):
        token = TokenManager.generate(self.bob, TokenType.LEVEL_ZERO)
        self.assertTrue(
            TokenManager.validate(self.bob, token, TokenType.LEVEL_ZERO))
        self.assertTrue(
            TokenManager.validate(self.bob, token, TokenType.LEVEL_ZERO))

    def test_TokenManager_validate_fails_on_wrong_kind(self):
        token = TokenManager.generate(self.bob, TokenType.LEVEL_ZERO)
        self.assertFalse(
            TokenManager.validate(self.bob, token, TokenType.LEVEL_ONE))

        token = TokenManager.generate(self.bob, TokenType.LEVEL_ONE)
        self.assertFalse(
            TokenManager.validate(self.bob, token, TokenType.LEVEL_ZERO))

    def test_TokenManager_validate_fails_on_wrong_user(self):
        token = TokenManager.generate(self.bob, TokenType.LEVEL_ZERO)
        self.assertFalse(
            TokenManager.validate(self.alice, token, TokenType.LEVEL_ZERO))
        self.assertTrue(
            TokenManager.validate(self.bob, token, TokenType.LEVEL_ZERO))
