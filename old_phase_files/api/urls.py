from django.urls import path
from . import views

urlpatterns = [
    # --- Teams Endpoints ---
    path("teams/", views.team_collection, name="team_collection"),
    path("teams/<int:team_id>/", views.team_detail, name="team_detail"),
    path(
        "teams/<int:team_id>/players/",
        views.player_collection,
        name="player_collection",
    ),
    path(
        "teams/<int:team_id>/players/<str:player_name>/",
        views.player_detail,
        name="player_detail",
    ),
    # --- Games Endpoints ---
    path("games/", views.game_collection, name="game_collection"),
    path("games/<int:game_id>/", views.game_detail, name="game_detail"),
    # --- Cup Endpoints ---
    path("cups/", views.cup_collection, name="cup_collection"),
    path("cups/<int:cup_id>/", views.cup_detail, name="cup_detail"),
    path("cups/<int:cup_id>/standings/", views.cup_standings, name="cup_standings"),
    path("cups/<int:cup_id>/gametree/", views.cup_gametree, name="cup_gametree"),
    path("cups/<int:cup_id>/games/", views.cup_games, name="cup_games"),
    path("cups/<int:cup_id>/playoffs/", views.cup_playoffs, name="cup_playoffs"),
]
