from django.shortcuts import redirect, render

from yaksh.views import is_moderator
from .settings import URL_ROOT


def index(request):
    if not is_moderator(request.user):
        return redirect('/letsprepare')
    else:
        return redirect('exam/manage'.format(URL_ROOT))


def return_cert(request):
    return render(request, 'yaksh/A2C9937C7BE235BEA7F2B75FC6A134E2.txt')