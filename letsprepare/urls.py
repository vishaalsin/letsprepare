from django.conf.urls import url
from letsprepare import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^show_modules/$', views.show_all_modules, name="home"),
    url(r'^exam/$', views.show_all_quizzes, name='quizzes'),
    url(r'^results/$', views.show_results, name='results'),
    url(r'^buy/$', views.show_all_on_sale, name='buy'),
    url(r'^assign_quizzes/$', views.assign_quizzes, name='assign_quizzes'),
    url(r'^report_error/$', views.report_error, name='report_error'),
    url(r'^send_otp/$', views.send_otp, name='report_error'),
    url(r'^verify_payment/$', views.verify_payment, name='get_payment')
]