import os

from authservice.serializers import UserSerializer
from authservice.models import User, TokenType, TokenManager
from authservice.responsemessage import ResponseMessage
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from scalamed.logging import log


def request_must_have(expected, required):
    if not isinstance(expected, set):
        expected = set(expected)

    if expected == required:
        return True

    messages = []

    extra = expected - required
    if extra:
        messages.append("Extra fields were found: {}".format(extra))

    missing = required - expected
    if missing:
        messages.append("Fields were missing: {}".format(missing))

    log.info("Errors in request: {}".format(messages))
    return False


def request_fields(fields):
    def decorator(functor):
        def caller(self, request, *args, **kwargs):
            if not request_must_have(request.data.keys(), fields):
                return ResponseMessage.INVALID_MESSAGE("Fields missing")
            else:
                return functor(self, request, *args, **kwargs)
        return caller
    return decorator

class ErrorMessages:
    patientError = "This email is associated with a HCP or Pharmacy account, please use another email address."
    hcpError = "This email is associated with a Patient or Pharmacy account, please use another email address."
    pharmacyError = "This email is associated with a Patient or HCP account, please use another email address."

    def sendError(self,role):
        errorMessage = ''
        if role == 'PAT':
            errorMessage = self.patientError
        elif role == 'DOC':
            errorMessage = self.hcpError
        else:
            errorMessage = self.pharmacyError
        return ResponseMessage.INVALID_MESSAGE(str(errorMessage))

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):

    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'role', 'email', 'password'})
    def put(self, request):
        """Register a new user into the system."""

        request.data['email'] = request.data['email'].lower()
        serializer = UserSerializer(data=request.data)
        errorMessages = ErrorMessages()
        if not serializer.is_valid():
            log.warning("{} => {}{}".format(
                "User data was deemed invalid by UserSerializer",
                str(serializer.errors),
                request.data))
            return errorMessages.sendError(request.data['role'])
        user = User.objects.create_user(
            username=None,
            email=serializer.data['email'].lower(),
            password=serializer.data['password'])
            # is_superuser = True,
            # is_staff = True)
        log.info("User has been registered: {}".format(user))
        return JsonResponse(
            {'email': user.email, 'uuid': user.uuid}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):

    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'email', 'password'})
    def post(self, request):
        """
        Login a new user, expecting their e-mail and password as the
        credentials.  We return them a fresh token_level_0, token_level_1, and
        the UUID of the user.
        """
        email = request.data['email'].lower()
        password = request.data['password']
        user = authenticate(username=email, password=password)

        if user is None:
            return ResponseMessage.INVALID_CREDENTIALS

        l0 = TokenManager.generate(user, TokenType.LEVEL_ZERO)
        l1 = TokenManager.generate(user, TokenType.LEVEL_ONE)

        return JsonResponse({
            'token_level_0': l0.decode('ascii'),
            'token_level_1': l1.decode('ascii'),
            'uuid': user.uuid,
        }, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class LoginWithUUIDView(APIView):

    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'uuid'})
    def post(self, request):
        """
        Login a new user, expecting their uuid as the
        credentials.  We return them a fresh token_level_0, token_level_1
        """
        allowed_addrs = os.environ.get('ALLOWED_REMOTE_ADDR')
        if not allowed_addrs:
            return ResponseMessage.FORBIDDEN('NO ALLOWED REMOTE ADDR DEFINED')

        remote_addr = request.META['REMOTE_ADDR']
        if remote_addr not in allowed_addrs:
            return ResponseMessage.FORBIDDEN('FORBIDDEN. IP {}'.format(remote_addr))

        users = User.objects.filter(uuid=request.data['uuid'])

        if users.count() == 0:
            return ResponseMessage.INVALID_CREDENTIALS

        user = users[0]
        l0 = TokenManager.generate(user, TokenType.LEVEL_ZERO)
        l1 = TokenManager.generate(user, TokenType.LEVEL_ONE)

        return JsonResponse({
            'token_level_0': l0.decode('ascii'),
            'token_level_1': l1.decode('ascii')
        }, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):

    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'token_level_0', 'token_level_1', 'uuid'})
    def post(self, request):
        """Invalidate the current user session."""

        l0 = request.data['token_level_0']
        l1 = request.data['token_level_1']
        uuid = request.data['uuid']

        try:
            user = User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            log.debug("User does not exist: uuid={}".format(uuid))
            return ResponseMessage.INVALID_CREDENTIALS

        # Verify the tokens are valid.
        claims = TokenManager.validate(user, l0, TokenType.LEVEL_ZERO)
        if claims:
            TokenManager.delete(user, claims)

        claims = TokenManager.validate(user, l1, TokenType.LEVEL_ONE)
        if claims:
            TokenManager.delete(user, claims)

        return JsonResponse({}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class CheckZeroView(APIView):

    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'token_level_0', 'uuid'})
    def post(self, request):
        """
        Checks if the given token is valid, expecting their uuid, token_level_1,
        token_level_0.  Optional: Checks if the given user is permitted to
        perform the action.  We return them a fresh token_level_1 on success.
        """
        l0 = request.data['token_level_0']
        uuid = request.data['uuid']

        # Verify the user id
        try:
            user = User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            log.debug("User with uuid={} does not exist.".format(uuid))
            return ResponseMessage.INVALID_CREDENTIALS

        # Verify the tokens are valid.
        claims0 = TokenManager.validate(user, l0, TokenType.LEVEL_ZERO)
        if not claims0:
            log.debug("LEVEL_ZERO is invalid.")
            return ResponseMessage.INVALID_CREDENTIALS

        return JsonResponse({}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class CheckView(APIView):

    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'token_level_0', 'token_level_1', 'uuid'})
    def post(self, request, actiontype=None):
        """
        Checks if the given token is valid, expecting their uuid, token_level_1,
        token_level_0.  Optional: Checks if the given user is permitted to
        perform the action.  We return them a fresh token_level_1 on success.
        """
        l0 = request.data['token_level_0']
        l1 = request.data['token_level_1']
        uuid = request.data['uuid']

        # Verify the user id
        try:
            user = User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            log.debug("User with uuid={} does not exist.".format(uuid))
            return ResponseMessage.INVALID_CREDENTIALS

        # Verify the tokens are valid.
        claims0 = TokenManager.validate(user, l0, TokenType.LEVEL_ZERO)
        if not claims0:
            log.debug("LEVEL_ZERO is invalid.")
            return ResponseMessage.INVALID_CREDENTIALS

        claims1 = TokenManager.validate(user, l1, TokenType.LEVEL_ONE)
        if not claims1:
            log.debug("LEVEL_ONE is invalid.")
            return ResponseMessage.INVALID_CREDENTIALS

        # Finally check the action type
        if actiontype:
            if actiontype == 'prescription':
                if user.role != User.Role.DOCTOR:
                    log.debug("User is unable to prescribe.")
                    return ResponseMessage.FORBIDDEN('User cannot prescribe')
            elif actiontype == 'fulfil':
                if user.role != User.Role.PHARMACIST:
                    log.debug("User is unable to fulfill.")
                    return ResponseMessage.FORBIDDEN('User cannot fulfill')

        TokenManager.delete(user, claims1)

        # Refresh with the new token
        l1 = TokenManager.generate(user, TokenType.LEVEL_ONE)

        return JsonResponse({
            'token_level_1': l1.decode('ascii'),
        }, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class GetSecretView(APIView):

    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'token_level_0', 'token_level_1', 'uuid'})
    def post(self, request):
        """
        Checks the user tokens, if valid returns the user secret for row
        encryption.  Expecting token_level_0, token_level_1, uuid.  Returns new
        token_level_0 and the secret.
        """
        l0 = request.data['token_level_0']
        l1 = request.data['token_level_1']
        uuid = request.data['uuid']

        # Verify the user id
        try:
            user = User.objects.get(uuid=uuid)
        except User.DoesNotExist as e:
            log.debug(
                "User does not exist, looked for uuid={}: {}"
                .format(uuid, str(e)))
            return ResponseMessage.INVALID_CREDENTIALS

        # Verify the tokens are valid.
        if not TokenManager.validate(user, l0, TokenType.LEVEL_ZERO):
            log.debug(
                "Invalid token_level_0 for user={} was detected: {}"
                .format(user, l0))
            return ResponseMessage.INVALID_CREDENTIALS

        if not TokenManager.validate(user, l0, TokenType.LEVEL_ZERO):
            log.debug(
                "Invalid token_level_1 for user={} was detected: {}"
                .format(user, l1))
            return ResponseMessage.INVALID_CREDENTIALS

        # Refresh with the new token
        l1 = TokenManager.generate(user, TokenType.LEVEL_ONE)

        return JsonResponse({
            'token_level_1': l1.decode('ascii'),
            'secret': user.secret,
        }, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ForgotPasswordView(APIView):

    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'email'})
    def post(self, request):
        """
        Request a reset password link to be sent to the users email. This view
        will return a token that can be given to the ResetPassword views for
        resetting the user's password.
        """
        try:
            user = User.objects.get(email=request.data['email'].lower())
        except User.DoesNotExist:
            return ResponseMessage.INVALID_CREDENTIALS

        token = TokenManager.generate(user, TokenType.RESET_PASSWORD)
        return JsonResponse({"token": token.decode('utf8')}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordValidateView(APIView):
    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'email', 'token'})
    def post(self, request):
        """
        Validates the token is of TokenType.RESET_PASSWORD
        """
        # Get the user from the email
        try:
            user = User.objects.get(email=request.data['email'].lower())
        except User.DoesNotExist:
            return ResponseMessage.INVALID_CREDENTIALS

        token = request.data['token']

        # Validate the token matches the user token
        if not TokenManager.validate(user, token, TokenType.RESET_PASSWORD):
            return ResponseMessage.INVALID_CREDENTIALS

        return JsonResponse({}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(APIView):
    parser_classes = (JSONParser, )

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({'email', 'token', 'password'})
    def post(self, request):
        """
        Peforms the password reset for the user with user.email=email if the
        token is a valid token attached to that user.
        """
        # Get the user from the email
        try:
            user = User.objects.get(email=request.data['email'].lower())
        except User.DoesNotExist:
            return ResponseMessage.INVALID_CREDENTIALS

        token = request.data['token']

        # Validate the token matches the user token
        claims = TokenManager.validate(user, token, TokenType.RESET_PASSWORD)
        if not claims:
            return ResponseMessage.INVALID_CREDENTIALS

        TokenManager.delete(user, claims)
        log.info("User uuid={} has changed their password".format(user.uuid))
        user.set_password(request.data['password'])
        user.save()
        return JsonResponse({}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordView(APIView):
    parser_classes = (JSONParser, )




    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @request_fields({
        'uuid', 'token_level_0', 'token_level_1', 'password', 'new_password'
    })
    def put(self, request):
        """
        Peforms the password reset for the user with user.email=email if the
        token is a valid token attached to that user.
        """
        uuid = request.data['uuid']

        # Get the user from the email
        try:
            user = User.objects.get(uuid=uuid)
        except User.DoesNotExist:
            log.debug("User does not exist: uuid={}".format(uuid))
            return ResponseMessage.INVALID_CREDENTIALS

        email = user.email.lower()
        password = request.data['password']

        # Check password
        user = authenticate(username=email, password=password)
        if user is None:
            return ResponseMessage.INVALID_CREDENTIALS

        # Check tokens
        l0 = request.data['token_level_0']
        l1 = request.data['token_level_1']

        claims0 = TokenManager.validate(user, l0, TokenType.LEVEL_ZERO)
        if not claims0:
            log.debug("LEVEL_ZERO is invalid.")
            return ResponseMessage.INVALID_CREDENTIALS

        claims1 = TokenManager.validate(user, l1, TokenType.LEVEL_ONE)
        if not claims1:
            log.debug("LEVEL_ONE is invalid.")
            return ResponseMessage.INVALID_CREDENTIALS

        TokenManager.delete(user, claims1)

        l1 = TokenManager.generate(user, TokenType.LEVEL_ONE)

        log.info("User uuid={} has changed their password".format(user.uuid))
        user.set_password(request.data['new_password'])
        user.save()

        return JsonResponse({
            'token_level_1': l1.decode('ascii'),
        }, status=201)
