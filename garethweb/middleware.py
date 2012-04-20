from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import SimpleLazyObject
from garethweb.models import User

def get_currentuser(request):
    if not hasattr(request, '_cached_currentuser'):
        request._cached_currentuser = None
        try:
            if 'user_id' in request.session:
                request._cached_currentuser = User.objects.get(id=request.session['user_id'])
        except ObjectDoesNotExist:
            del request.session['user_id']
    return request._cached_currentuser

class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.currentuser = SimpleLazyObject(lambda: get_currentuser(request))
