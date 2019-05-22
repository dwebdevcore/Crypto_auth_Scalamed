Auth Service
============

.. automodule:: authservice.models
    :members:

.. todo::

    Make the delete_token, create_token, and validate_token functions clearer to
    use and harder to stuff up using.


Example Usage
-------------

.. code-block:: python
    :linenos:

    >>> from authservice.models import User
    >>> user = User.objects.create_user(
        username=None,
        email="username@example.com",
        password="password123")
    >>> token = user.generate_token(level=0)
    >>> token
    b'eyJ0eXAiOiJKV1QiL...'
    >>>
    >>> user.validate_token(token) == True
    True
