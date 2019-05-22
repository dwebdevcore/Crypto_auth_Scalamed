from django.http import JsonResponse
from scalamed.logging import log

class ResponseMessage:
    """
    Utility file to handle simple error returns
    """
    INVALID_CREDENTIALS = JsonResponse({
        # TODO this should be removed, the status code covers it
        'success': False,
        'message': 'Your credentials were incorrect or invalid.',
    }, status=400)

    NOT_FOUND = JsonResponse({}, status=404)

    def INVALID_MESSAGE(msg):
        return JsonResponse({
            # TODO this should be removed, redundant, status code covers it
            'success': False,
            # TODO this should be changed to reason
            'message': msg
        }, status=400)

    def FORBIDDEN(reason):
        return JsonResponse({
            # TODO this should be changed to reason
            'message': reason
        }, status=403)
