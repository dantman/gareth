from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import SimpleLazyObject
from garethweb.models import User

def get_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = None
        try:
            if 'user_id' in request.session:
                request._cached_user = User.objects.get(id=request.session['user_id'])
        except ObjectDoesNotExist:
            del request.session['user_id']
    return request._cached_user

class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: get_user(request))
