# test_cup_elimination_standings.py
from datetime import timedelta
from team import Team
from cup import Cup, CupType
import json

print("=" * 60)
print("📊 ELIMINATION STANDINGS TEST")
print("=" * 60)

# 4 Takım oluştur
teams = [
    Team("Turkey"),
    Team("Serbia"),
    Team("Latvia"),
    Team("Finland")
]

# Oyuncular ekle
for team in teams:
    team.addplayer("Player1", 10)

# ELIMINATION cup oluştur
cup = Cup(teams, CupType.ELIMINATION, interval=timedelta(days=1))

print(f"\n{cup}")

# Test 1: Maçlar başlamadan
print("\n1️⃣ Maçlar başlamadan:")
standings = cup.standings()
print(json.dumps(standings, indent=2, ensure_ascii=False))

# Test 2: Semi-Final maçları oyna
print("\n2️⃣ Semi-Final maçları:")
game1 = cup.rounds[0][0]
game1.start()
game1.score(82, game1.home(), "Player1")
game1.score(65, game1.away(), "Player1")
game1.end()
print(f"   {game1.home().team_name} {game1.home_score} - {game1.away_score} {game1.away().team_name}")

game2 = cup.rounds[0][1]
game2.start()
game2.score(75, game2.home(), "Player1")
game2.score(73, game2.away(), "Player1")
game2.end()
print(f"   {game2.home().team_name} {game2.home_score} - {game2.away_score} {game2.away().team_name}")

# Standings
standings = cup.standings()
print("\n📊 Semi-Final Sonrası:")
for team_name in sorted(standings.keys()):
    info = standings[team_name]
    print(f"\n{team_name}:")
    print(f"   Round: {info['Round']}")
    print(f"   Won: {info['Won']}")
    print(f"   Lost: {info['Lost']}")

print("\n" + "=" * 60)
print("✅ TEST TAMAMLANDI!")
print("=" * 60)