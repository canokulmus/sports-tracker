# mysite/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Any URL starting with api/ goes to api.urls
    path("api/", include("api.urls")),
]
