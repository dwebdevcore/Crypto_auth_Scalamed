"""
This application is to be used be other developers. It is never to be used
directly by a user. Therefore, any erroneous input is a developers fault and
should be logged as an error. Warnings should be outputted if something that
might not be a developers fault occurs. Information should be output if
something permanent is occuring. Debugging should be output after a complex
operation, or where appropriate.

The configuration for logging lives within settings.py
"""

from logging import getLogger

log = getLogger('scalamed')


def logfunc(message):
    def decorator(function):
        def caller(*args, **kwargs):
            log.info(message)
            function(*args, **kwargs)
        return caller
    return decorator


def logroute(route=None, decoder=None, *args, **kwargs):
    def utf8decoder(request):
        return request.body.decode('utf8')

    if decoder == 'utf8':
        decoder = utf8decoder
    elif decoder == 'json':
        decoder = utf8decoder
    elif route is not None:
        decoder = utf8decoder

    def decorator(route):
        def caller(request, *args, **kwargs):
            log.debug(
                "{} {} => body =>\r\n{}"
                .format(
                    request.method,
                    request.get_full_path(),
                    decoder(request)))
            return route(request, *args, **kwargs)
        return caller

    if route is not None:
        return decorator(route)
    else:
        return decorator
