from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include("authentication.urls")),
    path('api/', include("api.urls")),
    path('rag/', include("rag.urls")),
]
