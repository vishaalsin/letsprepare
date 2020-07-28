from django.shortcuts import redirect, render

from yaksh.views import is_moderator
from .settings import URL_ROOT
from yaksh.models import Profile
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from yaksh.forms import PasswordResetForm

from letsprepare.views import send_sms

from allauth.account.forms import EmailAwarePasswordResetTokenGenerator
from allauth.account.utils import user_pk_to_url_str

def index(request):
    if not is_moderator(request.user):
        return redirect('/letsprepare')
    else:
        return redirect('exam/manage'.format(URL_ROOT))


def return_terms(request):
    return render(request, 'yaksh/terms_and_conditions.html')

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        country_code = request.POST['country_code']
        phone_number = request.POST['phone_number']
        token_generator = EmailAwarePasswordResetTokenGenerator()
        try:
            user = Profile.objects.get(phone_number = phone_number).user
            user_name = user.username
            temp_key = token_generator.make_token(user)
            user_str = user_pk_to_url_str(user)
            path = '/account/password/reset/key/' + '-'.join([user_str,temp_key])
            # path = reverse("account_reset_password_from_key",
            #                kwargs=dict(uidb36=user_pk_to_url_str(user), key=temp_key))
            number = "+" + country_code.split("-")[1] + phone_number
            link = request.build_absolute_uri().replace(request.get_full_path(), '') + path
            body = 'Hi There! Please go to following link to reset your password : \n' + link \
                    + '\n Your username is : ' + user_name
            send_sms(body,number)
            return render(request, 'registrations/password_reset_done.html')
        except:
            return render(request, 'registrations/password_reset_not_done.html')
    else:
        form = PasswordResetForm()
        return render(request, 'registrations/password_reset_form.html', context={'form' : form})