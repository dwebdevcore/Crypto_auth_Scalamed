

from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    """
    Overrides the default behaviour of the DjangoUserManager to use the email as
    the username, and remove the username from being considered as part of the
    model.
    """

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        This function is a copy of create_user() in Django-1.11. The major
        difference is validation occuring before a user is created; and the fact
        that the username is the email address.
        """
        assert(username is None)
        if not email:
            raise ValueError('The given email must be set')
        if not password:
            raise ValueError('The given password must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        username = None
        return self._create_user(username, email, password, **extra_fields)
