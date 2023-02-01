from django.urls import path, include
from .views import signin_view
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('signin/', signin_view, name="signin_view")
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
