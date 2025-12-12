# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Route for /api/teams/
    path("teams/", views.team_collection, name="teams_list"),
    # Route for /api/resources/123/
    # <int:resource_id> captures the number from the URL and passes it to the view
    path("resources/<int:resource_id>/", views.resource_detail, name="resource_detail"),
    # You will add more here for Games, Cups, etc.
    # path('games/', views.game_collection, ...),
]
