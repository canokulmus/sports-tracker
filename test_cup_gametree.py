from datetime import timedelta
from team import Team
from cup import Cup, CupType
import json

print("=" * 60)
print("🌳 GAMETREE METHOD TEST")
print("=" * 60)

# Test 1: 4 takım (2 round)
print("\n" + "=" * 60)
print("1️⃣ Test: 4 takım - gametree")
print("=" * 60)

teams_4 = [
    Team("Galatasaray"),
    Team("Fenerbahçe"),
    Team("Beşiktaş"),
    Team("Trabzonspor")
]

cup1 = Cup(teams_4, CupType.ELIMINATION, interval=timedelta(days=1))

tree1 = cup1.gametree()

print(f"\nGame Tree Yapısı:")
print(json.dumps(tree1, indent=2, ensure_ascii=False))

# Round isimleri kontrolü
assert "Semi-Final" in tree1, "Semi-Final olmalı!"
assert "Final" in tree1, "Final olmalı!"
print("\n✅ Round isimleri doğru")

# Her round'daki maç sayısı
assert len(tree1["Semi-Final"]) == 2, "Semi-Final'de 2 maç olmalı!"
assert len(tree1["Final"]) == 1, "Final'de 1 maç olmalı!"
print("✅ Maç sayıları doğru")

# Test 2: 8 takım (3 round)
print("\n" + "=" * 60)
print("2️⃣ Test: 8 takım - gametree")
print("=" * 60)

teams_8 = [Team(f"Team {i}") for i in range(1, 9)]
cup2 = Cup(teams_8, CupType.ELIMINATION, interval=timedelta(days=1))

tree2 = cup2.gametree()

print(f"\nGame Tree Yapısı:")
for round_name, games in tree2.items():
    print(f"\n{round_name}: {len(games)} maç")
    for game in games:
        print(f"   Game {game['game_id']}: {game['home']} vs {game['away']}")

# Round isimleri kontrolü
assert "Quarter-Final" in tree2, "Quarter-Final olmalı!"
assert "Semi-Final" in tree2, "Semi-Final olmalı!"
assert "Final" in tree2, "Final olmalı!"
print("\n✅ Round isimleri doğru")

# Her round'daki maç sayısı
assert len(tree2["Quarter-Final"]) == 4, "Quarter-Final'de 4 maç olmalı!"
assert len(tree2["Semi-Final"]) == 2, "Semi-Final'de 2 maç olmalı!"
assert len(tree2["Final"]) == 1, "Final'de 1 maç olmalı!"
print("✅ Maç sayıları doğru")

# Test 3: 16 takım (4 round)
print("\n" + "=" * 60)
print("3️⃣ Test: 16 takım - gametree")
print("=" * 60)

teams_16 = [Team(f"Team {i}") for i in range(1, 17)]
cup3 = Cup(teams_16, CupType.ELIMINATION, interval=timedelta(days=1))

tree3 = cup3.gametree()

print(f"\nRound İsimleri:")
for round_name in tree3.keys():
    print(f"   - {round_name}")

# Round isimleri kontrolü
assert "Round of 16" in tree3, "Round of 16 olmalı!"
assert "Quarter-Final" in tree3, "Quarter-Final olmalı!"
assert "Semi-Final" in tree3, "Semi-Final olmalı!"
assert "Final" in tree3, "Final olmalı!"
print("\n✅ Round isimleri doğru")

# Test 4: Game info detayları
print("\n" + "=" * 60)
print("4️⃣ Test: Game info detayları")
print("=" * 60)

first_game = tree1["Semi-Final"][0]
print(f"\nİlk maç bilgileri:")
print(f"   Game ID: {first_game['game_id']}")
print(f"   Home: {first_game['home']}")
print(f"   Away: {first_game['away']}")
print(f"   Date: {first_game['datetime']}")

# Gerekli key'ler var mı?
assert "game_id" in first_game, "game_id olmalı!"
assert "home" in first_game, "home olmalı!"
assert "away" in first_game, "away olmalı!"
assert "datetime" in first_game, "datetime olmalı!"
print("\n✅ Game info detayları tam")

# Test 5: LEAGUE tipinde hata vermeli
print("\n" + "=" * 60)
print("5️⃣ Test: LEAGUE tipinde hata kontrolü")
print("=" * 60)

cup_league = Cup(teams_4, CupType.LEAGUE, interval=timedelta(days=1))

try:
    tree_league = cup_league.gametree()
    print("❌ HATA: ValueError fırlatılmalıydı!")
    assert False, "LEAGUE tipinde gametree() hata vermeli!"
except ValueError as e:
    print(f"✅ Beklenen hata yakalandı: {e}")

# Test 6: Placeholder takımlar
print("\n" + "=" * 60)
print("6️⃣ Test: Placeholder takımlar gametree'de")
print("=" * 60)

final_game = tree2["Final"][0]
print(f"\nFinal maçı:")
print(f"   {final_game['home']} vs {final_game['away']}")

# Final'deki takımlar placeholder olmalı
assert "Winner" in final_game['home'], "Final'de placeholder olmalı!"
assert "Winner" in final_game['away'], "Final'de placeholder olmalı!"
print("✅ Placeholder takımlar gametree'de görünüyor")

# Test 7: JSON export
print("\n" + "=" * 60)
print("7️⃣ Test: JSON export")
print("=" * 60)

json_str = json.dumps(tree1, indent=2, ensure_ascii=False)
print(f"\nJSON uzunluğu: {len(json_str)} karakter")

# JSON parse edilebilir mi?
parsed = json.loads(json_str)
assert parsed == tree1, "JSON parse sonucu aynı olmalı!"
print("✅ JSON export çalışıyor")

# Test 8: 5 takım (bye ile)
print("\n" + "=" * 60)
print("8️⃣ Test: 5 takım - bye ile gametree")
print("=" * 60)

teams_5 = [Team(f"Team {i}") for i in range(1, 6)]
cup5 = Cup(teams_5, CupType.ELIMINATION, interval=timedelta(days=1))

tree5 = cup5.gametree()

print(f"\nGame Tree (5 takım):")
for round_name, games in tree5.items():
    print(f"\n{round_name}: {len(games)} maç")
    for game in games:
        print(f"   Game {game['game_id']}: {game['home']} vs {game['away']}")

print("\n✅ Bye durumunda da gametree çalışıyor")

print("\n" + "=" * 60)
print("🎉 TÜM GAMETREE TESTLERİ BAŞARIYLA GEÇTİ!")
print("=" * 60)