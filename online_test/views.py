from django.shortcuts import redirect

from yaksh.views import is_moderator
from .settings import URL_ROOT


def index(request):
    if not is_moderator(request.user):
        return redirect('/letsprepare')
    else:
        return redirect('exam/manage'.format(URL_ROOT))
