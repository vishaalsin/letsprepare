from django.conf.urls import url
from letsprepare import views

urlpatterns = [
    url(r'^$', views.show_all_exams, name="home"),
    url(r'^exam/$', views.show_all_quizzes, name='exam'),
    url(r'^examcrud/$', views.examCrud.as_view(), name='examCrud'),
]