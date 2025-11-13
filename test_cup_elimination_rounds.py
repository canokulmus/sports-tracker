# test_cup_elimination_rounds.py
from datetime import timedelta
from team import Team
from cup import Cup, CupType

print("=" * 60)
print("🏆 ELIMINATION - MULTIPLE ROUNDS TEST")
print("=" * 60)

# Test 1: 4 takım (2 round: yarı final + final)
print("\n" + "=" * 60)
print("1️⃣ Test: 4 takım - 2 round")
print("=" * 60)

teams_4 = [
    Team("Galatasaray"),
    Team("Fenerbahçe"),
    Team("Beşiktaş"),
    Team("Trabzonspor")
]

cup1 = Cup(teams_4, CupType.ELIMINATION, interval=timedelta(days=1))

print(f"\n{cup1}")
print(f"Toplam round sayısı: {len(cup1.rounds)}")
print(f"Toplam maç sayısı: {len(cup1.games)}")

# 4 takım: Round 1 (2 maç) + Round 2 Final (1 maç) = 3 maç
expected_total = 3
assert len(cup1.games) == expected_total, f"Beklenen {expected_total}, bulunan {len(cup1.games)}"
print(f"✅ Toplam maç sayısı doğru: {expected_total}")

print("\n📊 Round Detayları:")
for round_num, round_games in enumerate(cup1.rounds, 1):
    print(f"\n   Round {round_num}: {len(round_games)} maç")
    for game in round_games:
        print(f"      Game {game.id()}: {game.home().team_name} vs {game.away().team_name}")

# Test 2: 8 takım (3 round)
print("\n" + "=" * 60)
print("2️⃣ Test: 8 takım - 3 round")
print("=" * 60)

teams_8 = [
    Team(f"Team {i}") for i in range(1, 9)
]

cup2 = Cup(teams_8, CupType.ELIMINATION, interval=timedelta(days=1))

print(f"\n{cup2}")
print(f"Toplam round sayısı: {len(cup2.rounds)}")
print(f"Toplam maç sayısı: {len(cup2.games)}")

# 8 takım: R1(4) + R2(2) + R3(1) = 7 maç
expected_total_8 = 7
assert len(cup2.games) == expected_total_8, f"Beklenen {expected_total_8}, bulunan {len(cup2.games)}"
print(f"✅ Toplam maç sayısı doğru: {expected_total_8}")

print("\n📊 Round Detayları:")
for round_num, round_games in enumerate(cup2.rounds, 1):
    print(f"\n   Round {round_num}: {len(round_games)} maç")
    for game in round_games:
        print(f"      Game {game.id()}: {game.home().team_name} vs {game.away().team_name}")

# Test 3: Placeholder kontrolü
print("\n" + "=" * 60)
print("3️⃣ Test: Placeholder takım kontrolü")
print("=" * 60)

from team import PlaceholderTeam

# Round 2'deki takımlar placeholder olmalı
round2_game = cup2.rounds[1][0]  # İlk yarı final maçı
home_is_placeholder = isinstance(round2_game.home_, PlaceholderTeam)
away_is_placeholder = isinstance(round2_game.away_, PlaceholderTeam)

print(f"Round 2, Game {round2_game.id()}:")
print(f"   Home: {round2_game.home().team_name} (Placeholder: {home_is_placeholder})")
print(f"   Away: {round2_game.away().team_name} (Placeholder: {away_is_placeholder})")

assert home_is_placeholder, "Round 2 takımları placeholder olmalı!"
assert away_is_placeholder, "Round 2 takımları placeholder olmalı!"
print("✅ Placeholder takımlar doğru çalışıyor")

# Test 4: 16 takım (4 round)
print("\n" + "=" * 60)
print("4️⃣ Test: 16 takım - 4 round")
print("=" * 60)

teams_16 = [Team(f"Team {i}") for i in range(1, 17)]
cup3 = Cup(teams_16, CupType.ELIMINATION, interval=timedelta(days=1))

print(f"\n{cup3}")
print(f"Toplam round sayısı: {len(cup3.rounds)}")

# 16 takım: R1(8) + R2(4) + R3(2) + R4(1) = 15 maç
expected_rounds = 4
expected_total_16 = 15
assert len(cup3.rounds) == expected_rounds, f"Beklenen {expected_rounds} round, bulunan {len(cup3.rounds)}"
assert len(cup3.games) == expected_total_16, f"Beklenen {expected_total_16} maç, bulunan {len(cup3.games)}"
print(f"✅ Round sayısı doğru: {expected_rounds}")
print(f"✅ Toplam maç sayısı doğru: {expected_total_16}")

print("\n📊 Round Özeti:")
for round_num, round_games in enumerate(cup3.rounds, 1):
    print(f"   Round {round_num}: {len(round_games)} maç")

# Test 5: Tek sayıda takım (5 takım)
print("\n" + "=" * 60)
print("5️⃣ Test: 5 takım - bye ile")
print("=" * 60)

teams_5 = [Team(f"Team {i}") for i in range(1, 6)]
cup4 = Cup(teams_5, CupType.ELIMINATION, interval=timedelta(days=1))

print(f"\n{cup4}")
print(f"Toplam round sayısı: {len(cup4.rounds)}")
print(f"Toplam maç sayısı: {len(cup4.games)}")

# 5 takım: 1 bye + 4 oynar → R1(2) + R2(2) + R3(1) = 5 maç değil!
# Doğru: R1(2) + R2(1) + R3(1) = 4 maç
# Çünkü: 4 takım maç yapar → 2 kazanan + 1 bye = 3 takım → R2'de 1 maç (1 bye)
# → 2 kazanan → R3'te 1 final
print("\n📊 Round Detayları:")
for round_num, round_games in enumerate(cup4.rounds, 1):
    print(f"\n   Round {round_num}: {len(round_games)} maç")
    for game in round_games:
        print(f"      Game {game.id()}: {game.home().team_name} vs {game.away().team_name}")

print("\n" + "=" * 60)
print("✅ ELIMINATION ROUNDS TESTLERİ TAMAMLANDI!")
print("=" * 60)


""""
```

---

## 📊 Beklenen Çıktı (Kısaltılmış)
```
============================================================
🏆 ELIMINATION - MULTIPLE ROUNDS TEST
============================================================

============================================================
1️⃣ Test: 4 takım - 2 round
============================================================

Cup Tournament: ELIMINATION with 4 teams, 3 games
Toplam round sayısı: 2
Toplam maç sayısı: 3
✅ Toplam maç sayısı doğru: 3

📊 Round Detayları:

   Round 1: 2 maç
      Game 1: Team A vs Team B
      Game 2: Team C vs Team D

   Round 2: 1 maç
      Game 3: Winner of Game 1 vs Winner of Game 2

============================================================
2️⃣ Test: 8 takım - 3 round
============================================================

Cup Tournament: ELIMINATION with 8 teams, 7 games
Toplam round sayısı: 3
Toplam maç sayısı: 7
✅ Toplam maç sayısı doğru: 7

📊 Round Detayları:

   Round 1: 4 maç
      Game 1: Team 1 vs Team 2
      Game 2: Team 3 vs Team 4
      Game 3: Team 5 vs Team 6
      Game 4: Team 7 vs Team 8

   Round 2: 2 maç
      Game 5: Winner of Game 1 vs Winner of Game 2
      Game 6: Winner of Game 3 vs Winner of Game 4

   Round 3: 1 maç
      Game 7: Winner of Game 5 vs Winner of Game 6

============================================================
3️⃣ Test: Placeholder takım kontrolü
============================================================
Round 2, Game 5:
   Home: Winner of Game 1 (Placeholder: True)
   Away: Winner of Game 2 (Placeholder: True)
✅ Placeholder takımlar doğru çalışıyor

============================================================
✅ ELIMINATION ROUNDS TESTLERİ TAMAMLANDI!
============================================================
"""""