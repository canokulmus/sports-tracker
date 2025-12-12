# mysite/urls.py
from django.contrib import admin
from django.urls import path, include  # Import 'include'

urlpatterns = [
    path("admin/", admin.site.urls),  # You can ignore this
    # This tells Django: "Any URL starting with api/ goes to api.urls"
    path("api/", include("api.urls")),
]
