from authservice.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from scalamed.logging import log

DEBUG = False


class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        if DEBUG:
            print("")
            log.setLevel(10)
        else:
            log.setLevel(100)

    def tearDown(self):
        log.setLevel(30)

    def test_register(self):
        body = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        response = self.client.put('/auth/register', body, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('uuid', response.json())
        self.assertIn('email', response.json())

    def test_register_missing_password(self):
        body = {
            'email': 'jim.raynor@terran.scu',
        }

        response = self.client.put('/auth/register', body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_missing_password_blank_email(self):
        body = {
            'email': '',
        }

        response = self.client.put('/auth/register', body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_blank_email_blank_password(self):
        body = {
            'email': '',
            'password': ''
        }

        response = self.client.put('/auth/register', body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_double_register(self):
        body = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        response = self.client.put('/auth/register', body, format='json')
        self.assertEqual(response.status_code, 201)

        response = self.client.put('/auth/register', body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        body = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register
        response = self.client.put('/auth/register', body, format='json')

        # Log in
        response = self.client.post('/auth/login', body, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertIn('token_level_1', response.json())
        self.assertIn('token_level_0', response.json())
        self.assertIn('uuid', response.json())

    def test_check(self):

        body = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register and log in
        response = self.client.put('/auth/register', body, format='json')
        response = self.client.post('/auth/login', body, format='json')
        tokens = [response.json()['token_level_1']]

        # Check auth
        body = response.json()
        response = self.client.post('/auth/check', body, format='json')
        self.assertEqual(response.status_code, 200)

        # Only token_level_1 should be in check
        self.assertIn('token_level_1', response.json())
        self.assertNotIn('token_level_0', response.json())
        self.assertNotIn('uuid', response.json())
        tokens.append(response.json()['token_level_1'])

        # Check that original token_level_1 was invalidated and not reusable
        fail_response = self.client.post('/auth/check', body, format='json')
        self.assertEqual(fail_response.status_code, 400)

        # Check that our new token_level_1 works
        body['token_level_1'] = response.json()['token_level_1']
        response = self.client.post('/auth/check', body, format='json')
        self.assertEqual(response.status_code, 200)

        # Check that neither of the old ones work
        for token in tokens:
            body['token_level_1'] = token
            fail_response = self.client.post('/auth/check', body, format='json')
            self.assertEqual(fail_response.status_code, 400)

    def test_check_normal(self):

        body = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register and log in
        response = self.client.put('/auth/register', body, format='json')
        response = self.client.post('/auth/login', body, format='json')

        # Check auth
        body = response.json()

        auth = {
            'token_level_0': body['token_level_0'],
            'uuid': body['uuid'],
        }

        response = self.client.post('/auth/checkzero', auth, format='json')
        self.assertEqual(response.status_code, 200)

        # Check should just be 200
        self.assertNotIn('token_level_1', response.json())
        self.assertNotIn('token_level_0', response.json())
        self.assertNotIn('uuid', response.json())

        response = self.client.post('/auth/logout', body, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/auth/checkzero', auth, format='json')
        self.assertEqual(response.status_code, 400)

    def test_logout(self):

        body = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register and log in
        response = self.client.put('/auth/register', body, format='json')
        response = self.client.post('/auth/login', body, format='json')

        # Log out the user
        body = response.json()
        response = self.client.post('/auth/logout', body, format='json')
        self.assertEqual(response.status_code, 200)

        # {Token 0} and {Token 0, Token 1} shouldn't be authenticated anymore.
        response = self.client.post('/auth/check', body, format='json')
        self.assertEqual(response.status_code, 400)

    def test_multiple_logins(self):

        user_auth = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register and log in
        response = self.client.put('/auth/register', user_auth, format='json')
        response = self.client.post('/auth/login', user_auth, format='json')

        # Log out the user
        body = response.json()
        response = self.client.post('/auth/logout', body, format='json')
        self.assertEqual(response.status_code, 200)

        # {Token 0} and {Token 0, Token 1} shouldn't be authenticated anymore.
        response = self.client.post('/auth/check', body, format='json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/auth/login', user_auth, format='json')
        self.assertEqual(response.status_code, 200)

        body = response.json()
        response = self.client.post('/auth/check', body, format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_secret(self):
        user_details = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register and log in
        response = self.client.put(
            '/auth/register', user_details, format='json')
        uuid = response.json()['uuid']

        response = self.client.post('/auth/login', user_details, format='json')
        self.assertEquals(response.status_code, 200)

        # Get the tokens and uuid to use for further requests that require them
        body = response.json()
        response = self.client.post('/auth/getsecret', body, format='json')
        self.assertEquals(response.status_code, 200)

        self.assertIn('token_level_1', response.json())
        self.assertIn('secret', response.json())
        user_details['secret'] = response.json()['secret']

        user = User.objects.get(uuid=uuid)
        self.assertEqual(user.secret, user_details['secret'])

    def test_reset_password(self):
        user_details = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register a user
        response = self.client.put(
            '/auth/register', user_details, format='json')
        self.assertEquals(response.status_code, 201)

        # Run through the forgot password workflow
        response = self.client.post('/auth/forgotpw', {
            'email': user_details['email']
        }, format='json')

        self.assertEquals(response.status_code, 200)
        token = response.json()['token']

        response = self.client.post('/auth/resetpw/validate', {
            'email': user_details['email'],
            'token': token,
        }, format='json')
        self.assertEquals(response.status_code, 200)

        response = self.client.post('/auth/resetpw', {
            'email': user_details['email'],
            'token': token,
            'password': 'password123',
        }, format='json')
        self.assertEquals(response.status_code, 201)

        user_details['password'] = 'password123'

        response = self.client.post('/auth/login', user_details, format='json')
        self.assertEquals(response.status_code, 200)

    def test_change_password(self):
        user_details = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register a user
        response = self.client.put(
            '/auth/register', user_details, format='json')
        self.assertEquals(response.status_code, 201)

        response = self.client.post('/auth/login', user_details, format='json')
        self.assertEqual(response.status_code, 200)

        j = response.json()

        l0 = j['token_level_0']
        l1 = j['token_level_1']
        uuid = j['uuid']

        new_password = 'GkEZ0GxhQXVPG4glmhR7DM28EkKGX7Ry'

        body = {
            'uuid': uuid,
            'token_level_0': l0,
            'token_level_1': l1,
            'password': user_details['password'],
            'new_password': new_password
        }
        response = self.client.put('/auth/changepassword', body, format='json')
        self.assertEqual(response.status_code, 201)

    def test_change_password_incorrect_current_password(self):
        user_details = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register a user
        response = self.client.put(
            '/auth/register', user_details, format='json')
        self.assertEquals(response.status_code, 201)

        response = self.client.post('/auth/login', user_details, format='json')
        self.assertEqual(response.status_code, 200)

        j = response.json()

        l0 = j['token_level_0']
        l1 = j['token_level_1']
        uuid = j['uuid']

        new_password = 'GkEZ0GxhQXVPG4glmhR7DM28EkKGX7Ry'

        body = {
            'uuid': uuid,
            'token_level_0': l0,
            'token_level_1': l1,
            'password': user_details['password'] + 'a',
            'new_password': new_password
        }
        response = self.client.put('/auth/changepassword', body, format='json')

        self.assertEqual(response.status_code, 400)

    def test_change_password_bad_auth(self):
        user_details = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register a user
        response = self.client.put(
            '/auth/register', user_details, format='json')
        self.assertEquals(response.status_code, 201)

        response = self.client.post('/auth/login', user_details, format='json')
        self.assertEqual(response.status_code, 200)

        j = response.json()

        l0 = j['token_level_0']
        uuid = j['uuid']

        new_password = 'GkEZ0GxhQXVPG4glmhR7DM28EkKGX7Ry'

        body = {
            'uuid': uuid,
            'token_level_0': l0,
            'token_level_1': l0,
            'password': user_details['password'],
            'new_password': new_password
        }
        response = self.client.put('/auth/changepassword', body, format='json')

        self.assertEqual(response.status_code, 400)

    def test_change_password_wrong_uuid(self):
        user_details = {
            'email': 'jim.raynor@terran.scu',
            'password': 'wXqkw5UCLOqxrNQrl2Xe2sgNR4JtOFjR'
        }

        # Register a user
        response = self.client.put(
            '/auth/register', user_details, format='json')
        self.assertEquals(response.status_code, 201)

        response = self.client.post('/auth/login', user_details, format='json')
        self.assertEqual(response.status_code, 200)

        j = response.json()

        l0 = j['token_level_0']
        l1 = j['token_level_1']
        uuid = j['uuid']

        new_password = 'GkEZ0GxhQXVPG4glmhR7DM28EkKGX7Ry'

        uuid = ('8' if uuid[0] != '8' else '7') + uuid[1:]

        body = {
            'uuid': uuid,
            'token_level_0': l0,
            'token_level_1': l1,
            'password': user_details['password'],
            'new_password': new_password
        }
        response = self.client.put('/auth/changepassword', body, format='json')

        self.assertEqual(response.status_code, 400)
