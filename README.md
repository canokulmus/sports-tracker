# Sports Tournament Management System

A comprehensive Python library for managing sports tournaments with support for multiple tournament formats, real-time score tracking, and observer pattern implementation.

## 🎯 Project Overview

This project implements a complete tournament management system as part of **CENG445**. The system supports three tournament types (LEAGUE, ELIMINATION, GROUP), provides real-time game tracking with observer pattern, and includes a centralized repository for object management.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Usage Examples](#usage-examples)
- [API Documentation](#api-documentation)
- [Design Patterns](#design-patterns)
- [Requirements](#requirements)

---

## ✨ Features

### Core Functionality

- ✅ **Team Management**: Create teams, add/remove players, set custom attributes
- ✅ **Game Tracking**: Start, pause, resume, end games with timeline tracking
- ✅ **Tournament Types**:
  - **LEAGUE**: Round-robin format where every team plays every other team
  - **ELIMINATION**: Single/double elimination bracket tournaments
  - **GROUP**: Group stage + playoff elimination format
- ✅ **Observer Pattern**: Real-time notifications for game state changes
- ✅ **Repository Pattern**: Centralized object creation and lifecycle management
- ✅ **Search & Query**: Filter games by team, date range, or group
- ✅ **Statistics**: Live standings, game trees, and player statistics

### Advanced Features

- 📊 Dynamic standings calculation for all tournament types
- 🌳 Tournament bracket visualization (gametree)
- 👥 Multi-user object attachment system
- ⏱️ Precise time tracking with pause/resume support
- 📝 Complete timeline of all game events
- 🔍 Flexible search with multiple filter criteria

---

## 📁 Project Structure

```
phase1/
├── constants.py          # Game constants and messages
├── helpers.py            # Helper functions for time, player, score tracking
├── team.py              # Team and PlaceholderTeam classes
├── game.py              # Game class with observer pattern
├── cup.py               # Cup class supporting 3 tournament types
├── repo.py              # Repository for object management
├── main.py              # Comprehensive demonstration
├── test_team.py         # Unit tests for Team class (11 tests)
├── test_game.py         # Unit tests for Game class (15 tests)
├── test_cup.py          # Unit tests for Cup class (19 tests)
├── test_repo.py         # Unit tests for Repo class (21 tests)
├── pyrightconfig.json   # Type checking configuration
└── README.md            # This file
```

**Total: 66 unit tests covering all functionality**

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project:**

```bash
cd phase1
```

2. **Install pytest (for running tests):**

```bash
pip3 install pytest
# or
pip3 install --user pytest
# or if externally-managed error:
pip3 install pytest --break-system-packages
```

3. **Verify installation:**

```bash
python3 --version  # Should be 3.10+
pytest --version   # Should show pytest version
```

---

## 🎬 Quick Start

### Run the Demo

```bash
python3 main.py
```

This will demonstrate:

- Repository object management
- LEAGUE tournament with standings
- ELIMINATION tournament with brackets
- Observer pattern for live game updates
- Search functionality

### Run Unit Tests

```bash
# Run all tests
pytest -v

# Run specific test file
pytest test_team.py -v
pytest test_game.py -v
pytest test_cup.py -v
pytest test_repo.py -v

# Run tests with coverage
pytest --cov=. -v
```

**Expected result:** ✅ 66/66 tests passing

---

## 💡 Usage Examples

### Example 1: Create and Play a Game

```python
from datetime import datetime
from team import Team
from game import Game

# Create teams
home = Team("Galatasaray")
home.addplayer("Icardi", 9)

away = Team("Fenerbahçe")
away.addplayer("Dzeko", 9)

# Create and play game
game = Game(home, away, id_=1, datetime=datetime.now())
game.start()
game.score(2, home, "Icardi")
game.score(1, away, "Dzeko")
game.end()

# Get statistics
stats = game.stats()
print(f"Final Score: {stats['Home']['Pts']} - {stats['Away']['Pts']}")
```

### Example 2: Create a League Tournament

```python
from datetime import timedelta
from team import Team
from cup import Cup, CupType

# Create teams
teams = [
    Team("Team A"),
    Team("Team B"),
    Team("Team C"),
    Team("Team D")
]

# Create league (round-robin)
cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))

# Play games and get standings
for game in cup.games:
    game.start()
    game.score(3, game.home())
    game.score(1, game.away())
    game.end()

standings = cup.standings()
for pos, (team, won, draw, lost, gf, ga, pts) in enumerate(standings, 1):
    print(f"{pos}. {team}: {pts} points")
```

### Example 3: Observer Pattern

```python
class GameObserver:
    def update(self, game):
        print(f"Game {game.id()} updated: {game.state.name}")

observer = GameObserver()
game.watch(observer)

game.start()  # Observer notified
game.end()    # Observer notified
```

### Example 4: Search Games

```python
# Search by team name
games = cup.search(tname="Team A")

# Search by date range
from datetime import datetime, timedelta
start = datetime.now()
end = start + timedelta(days=7)
games = cup.search(between=(start, end))

# Get specific game by ID
game = cup[1]
```

---

## 📚 API Documentation

### Team Class

```python
Team(name: str)
```

**Methods:**

- `addplayer(name: str, no: int)` - Add a player to the team
- `delplayer(name: str)` - Remove a player from the team
- `team[key] = value` - Set custom team attribute
- `team.attribute` - Get custom team attribute

### Game Class

```python
Game(home: Team, away: Team, id_: int, datetime: datetime, group: str | None = None)
```

**Methods:**

- `start()` - Start the game
- `pause()` - Pause the game
- `resume()` - Resume paused game
- `end()` - End the game
- `score(points: int, team: Team, player: str | None)` - Add score
- `watch(observer)` - Add observer for notifications
- `unwatch(observer)` - Remove observer
- `stats()` - Get game statistics
- `id()` - Get game ID
- `home()` - Get home team
- `away()` - Get away team

### Cup Class

```python
Cup(teams: List[Team], type: str, interval: timedelta,
    num_groups: int = 4, playoff_teams: int = 8)
```

**Tournament Types:**

- `CupType.LEAGUE` - Round-robin, single match
- `CupType.LEAGUE2` - Round-robin, double match (home/away)
- `CupType.ELIMINATION` - Single elimination
- `CupType.ELIMINATION2` - Double elimination (home/away)
- `CupType.GROUP` - Group stage + playoffs
- `CupType.GROUP2` - Group stage + double playoffs

**Methods:**

- `search(tname=None, group=None, between=None)` - Search games
- `cup[game_id]` - Get game by ID
- `standings()` - Get tournament standings
- `gametree()` - Get tournament bracket (ELIMINATION/GROUP only)
- `watch(observer, **searchparams)` - Add observer for matching games
- `unwatch(observer)` - Remove observer

### Repo Class

```python
Repo()
```

**Methods:**

- `create(type="team"|"game"|"cup", **kwargs)` - Create and register object
- `list()` - List all objects as (id, description) pairs
- `attach(id, user="Polat Alemdar")` - Attach user to object
- `detach(id, user)` - Detach user from object
- `delete(id)` - Delete unattached object
- `listattached(user)` - List objects attached by user

---

## 🎨 Design Patterns

### 1. Observer Pattern

Games notify observers when state changes (start, pause, resume, end, score).

```python
class MyObserver:
    def update(self, game):
        print(f"Game updated: {game.state}")

game.watch(MyObserver())
```

### 2. Repository Pattern

Centralized object creation and lifecycle management with reference counting.

```python
repo = Repo()
team_id = repo.create(type="team", name="Arsenal")
repo.attach(team_id, "Coach")
repo.detach(team_id, "Coach")
repo.delete(team_id)
```

### 3. Factory Pattern

Repo acts as a factory for creating different object types.

```python
team_id = repo.create(type="team", name="Bayern")
game_id = repo.create(type="game", home=team1, away=team2, datetime=now())
```

---

## 📦 Requirements

### Python Version

- Python 3.10 or higher (uses modern type hints with `|` operator)

### External Dependencies

- **pytest** >= 7.0.0 (for running unit tests)
- **pluggy** (pytest dependency, auto-installed)

### Standard Library Dependencies

- `datetime` - Date and time handling
- `time` - Monotonic time tracking
- `typing` - Type hints
- `itertools` - Combinations for match generation
- `random` - Random team shuffling
- `string` - Group name generation
- `json` - JSON export (used in tests)

---

## 🧪 Testing

### Test Coverage

| Module         | Tests  | Coverage                           |
| -------------- | ------ | ---------------------------------- |
| `test_team.py` | 11     | Team class, PlaceholderTeam        |
| `test_game.py` | 15     | Game lifecycle, scoring, observers |
| `test_cup.py`  | 19     | LEAGUE, ELIMINATION, GROUP         |
| `test_repo.py` | 21     | CRUD, attach/detach, listing       |
| **Total**      | **66** | **All core functionality**         |

### Running Tests

```bash
# All tests
pytest -v

# Specific class
pytest test_cup.py::TestCupLeague -v

# With output
pytest -v -s

# Stop on first failure
pytest -x

# Run in parallel (if pytest-xdist installed)
pytest -n auto
```

---

## 🏆 Tournament Types Explained

### LEAGUE (Round-Robin)

Every team plays against every other team once (or twice for LEAGUE2).

**Example:** 4 teams → 6 games (C(4,2) = 6)

```
Team A vs Team B
Team A vs Team C
Team A vs Team D
Team B vs Team C
Team B vs Team D
Team C vs Team D
```

**Standings:** Sorted by points, then goal difference

- Win: 2 points
- Draw: 1 point
- Loss: 0 points

### ELIMINATION (Knockout)

Single/double elimination bracket. Losers are eliminated.

**Example:** 8 teams → 7 games

```
Quarter-Finals (4 games) → Semi-Finals (2 games) → Final (1 game)
```

**Features:**

- Bye system for odd number of teams
- Placeholder teams for future rounds
- Dynamic bracket generation

### GROUP (Group Stage + Playoffs)

Teams divided into groups, top teams advance to playoffs.

**Example:** 16 teams, 4 groups, 8 playoffs

```
Groups A,B,C,D (4 teams each) → Top 2 from each group → 8-team playoff
```

**Formula:**

- k = ⌊playoff_teams / num_groups⌋ teams per group
- Wild cards = playoff_teams - (k × num_groups)

---

## 📝 Notes

### Game Time Tracking

- Uses `monotonic()` for accurate time measurement
- Paused time is excluded from total game time
- Format: `MM:SS.ff` (e.g., "45:23.50")
- Shows "Full Time" when game ends

### Observer Notifications

Observers are notified on:

- `start()` - Game starts
- `pause()` - Game pauses
- `resume()` - Game resumes
- `end()` - Game ends
- `score()` - Points scored

### Placeholder Teams

Used in ELIMINATION rounds to represent future winners:

```python
PlaceholderTeam("Winner of Game 1", [1])
PlaceholderTeam("Winner of Games [1, 2]", [1, 2])
```

---

**Status:** ✅ Complete - All tests passing (66/66)
