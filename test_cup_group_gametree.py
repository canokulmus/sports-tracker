# test_cup_group_gametree.py
from datetime import timedelta
from team import Team
from cup import Cup, CupType
import json

print("=" * 60)
print("🌳 GROUP GAMETREE TEST")
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

# Test 1: gametree (sadece grup maçları)
print("\n" + "=" * 60)
print("1️⃣ Test: Gametree (grup maçları)")
print("=" * 60)

tree = cup.gametree()

print("\n📊 Tree structure:")
print(f"   Groups: {list(tree['Groups'].keys())}")
print(f"   Playoffs: {list(tree['Playoffs'].keys())}")

# Her grup için maç sayısı
for group_name, games in tree["Groups"].items():
    print(f"\n   Group {group_name}: {len(games)} games")
    assert len(games) == 6, f"Group {group_name} should have 6 games (C(4,2))"

print("\n✅ Grup maçları gametree'de doğru")

# Test 2: Playoff ekledikten sonra
print("\n" + "=" * 60)
print("2️⃣ Test: Playoff ile gametree")
print("=" * 60)

# Grup maçlarını oyna
print("\n🎮 Grup maçları oynanıyor...")
for group_games in cup.group_games.values():
    for game in group_games:
        game.start()
        import random
        game.score(random.randint(70, 100), game.home(), "Player")
        game.score(random.randint(60, 90), game.away(), "Player")
        game.end()

# Playoff oluştur
cup.generate_playoffs()

# Yeni gametree
tree2 = cup.gametree()

print("\n📊 Tree with Playoffs:")
print(f"   Groups: {len(tree2['Groups'])} groups")

# Playoff kontrolü
if tree2["Playoffs"]:
    print(f"   Playoffs: {list(tree2['Playoffs'].keys())}")
    for round_name, games in tree2["Playoffs"].items():
        print(f"      {round_name}: {len(games)} games")
        for game in games:
            print(f"         Game {game['game_id']}: {game['home']} vs {game['away']}")
else:
    print("   Playoffs: Empty")

assert len(tree2["Playoffs"]) > 0, "Playoff olmalı!"
print("\n✅ Playoff gametree'de görünüyor")

# Test 3: JSON export
print("\n" + "=" * 60)
print("3️⃣ Test: JSON export")
print("=" * 60)

json_str = json.dumps(tree2, indent=2, ensure_ascii=False)
print(f"\nJSON uzunluğu: {len(json_str)} karakter")

# Sadece Groups/A'yı göster (örnek)
print("\nGroup A games (first 2):")
for game in tree2["Groups"]["A"][:2]:
    print(f"   Game {game['game_id']}: {game['home']} vs {game['away']}")

print("\n✅ JSON export çalışıyor")

# Test 4: LEAGUE tipinde hata vermeli
print("\n" + "=" * 60)
print("4️⃣ Test: LEAGUE tipinde hata kontrolü")
print("=" * 60)

teams_league = [Team(f"Team {i}") for i in range(1, 5)]
cup_league = Cup(teams_league, CupType.LEAGUE, interval=timedelta(days=1))

try:
    tree_league = cup_league.gametree()
    print("❌ HATA: ValueError fırlatılmalıydı!")
    assert False
except ValueError as e:
    print(f"✅ Beklenen hata: {e}")

print("\n" + "=" * 60)
print("🎉 GROUP GAMETREE TESTİ TAMAMLANDI!")
print("=" * 60)