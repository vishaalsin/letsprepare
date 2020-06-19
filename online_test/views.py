from django.shortcuts import redirect

from .settings import URL_ROOT


def index(request):
    return redirect('letsprepare/'.format(URL_ROOT))
