from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from online_test import views
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'online_test.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('allauth.urls')),
    url(r'^reset_password/', views.reset_password, name='reset_password'),
    url(r'^terms/', views.return_terms, name='terms'),
    url(r'^$', views.index, name='index'),
    url(r'^exam/', include(('yaksh.urls', 'yaksh'))),
    url(r'^exam/reset/', include('django.contrib.auth.urls')),
    url(r'^', include('social_django.urls', namespace='social')),
    url(r'^grades/', include(('grades.urls', 'grades'))),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^letsprepare/', include(('letsprepare.urls', 'letsprepare'), namespace='letsprepare')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
