from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponse

def home(request):
    return HttpResponse("Página Inicial")

urlpatterns = [
    path('', home), 
    path('api/v1/accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
