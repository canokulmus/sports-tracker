# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # When user visits /api/teams/, call the team_collection function
    path("teams/", views.team_collection, name="teams_list"),
]
