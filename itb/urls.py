from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^battles/', include('battles.urls', namespace='battles')),
    url(r'^admin/', include(admin.site.urls)),
)

