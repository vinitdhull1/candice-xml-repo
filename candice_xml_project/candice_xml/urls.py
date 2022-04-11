from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', views.index, name='index'),
    path('candice_xml', views.candice_xml, name='candice_xml'),
    path('candice_xml/login', views.log_in, name='login'),
    path('candice_xml/logout', views.log_out, name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)