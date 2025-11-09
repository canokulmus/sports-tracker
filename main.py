from datetime import datetime
from repo import Repo


def main():
    """
    Demonstrates the creation and management of teams and games
    using the Repo class.
    """
    print("Initializing Sports Tracker...")
    repo = Repo()

    # 1. Create two teams
    print("\n--- Creating Teams ---")
    home_team_id = repo.create(type="team", name="Golden State Warriors")
    away_team_id = repo.create(type="team", name="Los Angeles Lakers")

    home_team = repo.attach(home_team_id)["instance"]
    away_team = repo.attach(away_team_id)["instance"]

    home_team.addplayer("Stephen Curry", 30)
    away_team.addplayer("LeBron James", 23)

    print(f"Created Team: {home_team.team_name} with ID {home_team_id}")
    print(f"Created Team: {away_team.team_name} with ID {away_team_id}")

    # 2. Create a game between the two teams
    print("\n--- Creating Game ---")
    game_id = repo.create(
        type="game", home=home_team, away=away_team, datetime=datetime.now()
    )
    game = repo.attach(game_id)["instance"]
    print(
        f"Game created with ID {game.id()} between {game.home().team_name} and {game.away().team_name}"
    )

    # 3. Demonstrate the game lifecycle
    print(f"\n--- Game Lifecycle Demo (Game ID: {game.id()}) ---")
    print(f"Initial state: {game.state.name}")
    game.start()
    print(f"State after start(): {game.state.name}")
    game.pause()
    print(f"State after pause(): {game.state.name}")
    game.resume()
    print(f"State after resume(): {game.state.name}")


if __name__ == "__main__":
    main()
