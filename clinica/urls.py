from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/pacientes/', permanent=False), name='inicio'),
    path('cuentas/', include('cuentas.urls')),
    path('pacientes/', include('pacientes.urls')),
    path('consulta/', include('consulta.urls')),
    path('facturacion/', include('facturacion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
