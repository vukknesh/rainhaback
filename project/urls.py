
from django.contrib import admin
from django.conf.urls import url, include as inc
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('userprofile.urls')),
    path('api/books/', include('book.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
