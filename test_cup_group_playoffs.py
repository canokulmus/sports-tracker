# test_cup_group_playoffs.py
from datetime import timedelta
from team import Team
from cup import Cup, CupType

print("=" * 60)
print("🏆 GROUP PLAYOFFS TEST")
print("=" * 60)

# 16 takım oluştur
teams = [Team(f"Team {i}") for i in range(1, 17)]
for team in teams:
    team.addplayer("Player", 10)

# GROUP cup oluştur
cup = Cup(
    teams, 
    CupType.GROUP, 
    interval=timedelta(days=1),
    num_groups=4,
    playoff_teams=8
)

print(f"\n{cup}")
print(f"Grup maçları: {len(cup.games)}")

# Test 1: Grup maçlarını oyna
print("\n" + "=" * 60)
print("1️⃣ Test: Grup maçlarını oyna")
print("=" * 60)

for group_name, group_games in cup.group_games.items():
    print(f"\n🎮 Group {group_name} maçları oynanıyor...")
    for game in group_games:
        game.start()
        # Ev sahibi kazansın (rastgele skorlar)
        import random
        home_score = random.randint(70, 100)
        away_score = random.randint(60, 90)
        game.score(home_score, game.home(), "Player")
        game.score(away_score, game.away(), "Player")
        game.end()

print("\n✅ Tüm grup maçları bitti")

# Test 2: Standings
print("\n" + "=" * 60)
print("2️⃣ Test: Grup standings")
print("=" * 60)

standings = cup.standings()
print("\n📊 Grup Tabloları:")
for group_name, group_standings in standings["Groups"].items():
    print(f"\nGroup {group_name}:")
    for i, (team_name, won, draw, lost, gf, ga, pts) in enumerate(group_standings, 1):
        print(f"   {i}. {team_name}: {pts} pts (W:{won} D:{draw} L:{lost})")

# Test 3: Playoff oluştur
print("\n" + "=" * 60)
print("3️⃣ Test: Playoff oluştur")
print("=" * 60)

cup.generate_playoffs()

print(f"\n📊 Playoff maç sayısı: {len(cup.playoff_games)}")
print(f"📊 Toplam maç sayısı: {len(cup.games)}")

assert len(cup.playoff_games) == 4, "8 takım playoff → 4 maç (ilk tur)"

print("\n✅ Playoff maçları oluşturuldu")

print("\n" + "=" * 60)
print("🎉 GROUP PLAYOFFS TEST TAMAMLANDI!")
print("=" * 60)