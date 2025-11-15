
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from CodeMap.urls import urlpatterns1
from django.conf.urls import handler404, handler500

urlpatterns = [
        path('admin/', admin.site.urls),
    path("",include(urlpatterns1)),
    
] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
handler404 = 'CodeMap.views.custom_404'
handler500 = 'CodeMap.views.custom_500'

handler400 = 'CodeMap.views.custom_400'