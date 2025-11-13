# test_cup_elimination.py
from datetime import timedelta
from team import Team
from cup import Cup, CupType

print("=" * 60)
print("🏆 ELIMINATION CUP TEST (Basit Versiyon)")
print("=" * 60)

# Test 1: 4 Takım (Çift sayı)
print("\n" + "=" * 60)
print("1️⃣ Test: 4 takım ile ELIMINATION")
print("=" * 60)

teams_4 = [
    Team("Galatasaray"),
    Team("Fenerbahçe"),
    Team("Beşiktaş"),
    Team("Trabzonspor")
]

cup1 = Cup(teams_4, CupType.ELIMINATION, interval=timedelta(days=1))

print(f"\n{cup1}")
print(f"Takım sayısı: {len(teams_4)}")
print(f"Maç sayısı: {len(cup1.games)}")

# 4 takım → 2 maç (yarı final)
# Formül: n / 2 (ilk tur için)
expected_games_round1 = len(teams_4) // 2
assert len(cup1.games) == expected_games_round1, f"Beklenen {expected_games_round1}, bulunan {len(cup1.games)}"
print(f"✅ Maç sayısı doğru: {expected_games_round1}")

print("\n📋 İlk Tur Maçları:")
for i, game in enumerate(cup1.games, 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name} (ID: {game.id()})")

# Test 2: 8 Takım
print("\n" + "=" * 60)
print("2️⃣ Test: 8 takım ile ELIMINATION")
print("=" * 60)

teams_8 = [
    Team("Galatasaray"),
    Team("Fenerbahçe"),
    Team("Beşiktaş"),
    Team("Trabzonspor"),
    Team("Başakşehir"),
    Team("Antalyaspor"),
    Team("Konyaspor"),
    Team("Sivasspor")
]

cup2 = Cup(teams_8, CupType.ELIMINATION, interval=timedelta(days=1))

print(f"\n{cup2}")
print(f"Takım sayısı: {len(teams_8)}")
print(f"Maç sayısı: {len(cup2.games)}")

expected_games_8 = len(teams_8) // 2  # 4 maç (çeyrek final)
assert len(cup2.games) == expected_games_8, f"Beklenen {expected_games_8}, bulunan {len(cup2.games)}"
print(f"✅ Maç sayısı doğru: {expected_games_8}")

print("\n📋 İlk Tur Maçları:")
for i, game in enumerate(cup2.games, 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name} (ID: {game.id()})")

# Test 3: Tek sayıda takım (5 takım)
print("\n" + "=" * 60)
print("3️⃣ Test: 5 takım ile ELIMINATION (bye var)")
print("=" * 60)

teams_5 = [
    Team("Galatasaray"),
    Team("Fenerbahçe"),
    Team("Beşiktaş"),
    Team("Trabzonspor"),
    Team("Başakşehir")
]

cup3 = Cup(teams_5, CupType.ELIMINATION, interval=timedelta(days=1))

print(f"\n{cup3}")
print(f"Takım sayısı: {len(teams_5)}")
print(f"Maç sayısı: {len(cup3.games)}")

# 5 takım → 1 bye, 4 takım maç yapar → 2 maç
expected_games_5 = (len(teams_5) - 1) // 2  # 2 maç
assert len(cup3.games) == expected_games_5, f"Beklenen {expected_games_5}, bulunan {len(cup3.games)}"
print(f"✅ Maç sayısı doğru: {expected_games_5}")

print("\n📋 İlk Tur Maçları:")
for i, game in enumerate(cup3.games, 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name} (ID: {game.id()})")

# Test 4: ELIMINATION2 (çift maç)
print("\n" + "=" * 60)
print("4️⃣ Test: ELIMINATION2 (her eşleşme 2 maç)")
print("=" * 60)

cup4 = Cup(teams_4, CupType.ELIMINATION2, interval=timedelta(days=1))

print(f"\n{cup4}")
print(f"Maç sayısı: {len(cup4.games)}")

# 4 takım → 2 eşleşme → 4 maç (her eşleşme 2 maç)
expected_games_double = len(teams_4)  # 4 maç
assert len(cup4.games) == expected_games_double, f"Beklenen {expected_games_double}, bulunan {len(cup4.games)}"
print(f"✅ Maç sayısı doğru: {expected_games_double}")

print("\n📋 İlk Tur Maçları (rövanş dahil):")
for i, game in enumerate(cup4.games, 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name} (ID: {game.id()})")

# Test 5: Rastgele eşleştirme kontrolü
print("\n" + "=" * 60)
print("5️⃣ Test: Rastgele eşleştirme")
print("=" * 60)

# Aynı takımlarla 3 kez cup oluştur
print("Aynı takımlarla 3 farklı cup oluşturuluyor...")

cup_a = Cup(teams_4.copy(), CupType.ELIMINATION, interval=timedelta(days=1))
cup_b = Cup(teams_4.copy(), CupType.ELIMINATION, interval=timedelta(days=1))
cup_c = Cup(teams_4.copy(), CupType.ELIMINATION, interval=timedelta(days=1))

matchup_a = f"{cup_a.games[0].home().team_name} vs {cup_a.games[0].away().team_name}"
matchup_b = f"{cup_b.games[0].home().team_name} vs {cup_b.games[0].away().team_name}"
matchup_c = f"{cup_c.games[0].home().team_name} vs {cup_c.games[0].away().team_name}"

print(f"Cup A ilk maç: {matchup_a}")
print(f"Cup B ilk maç: {matchup_b}")
print(f"Cup C ilk maç: {matchup_c}")

# En az biri farklı olmalı (rastgele karıştırma çalışıyor)
all_same = (matchup_a == matchup_b == matchup_c)
if not all_same:
    print("✅ Rastgele eşleştirme çalışıyor!")
else:
    print("⚠️  Üç denemede de aynı eşleştirme (olasılık düşük ama olabilir)")

print("\n" + "=" * 60)
print("✅ ELIMINATION İLK TUR TESTLERİ BAŞARIYLA GEÇTİ!")
print("=" * 60)
print("\nNOT: Şu an sadece ilk tur maçları oluşturuluyor.")
print("Sonraki turlar (yarı final, final) henüz implement edilmedi.")
"""""
```

---

## 📊 Beklenen Çıktı
```
============================================================
🏆 ELIMINATION CUP TEST (Basit Versiyon)
============================================================

============================================================
1️⃣ Test: 4 takım ile ELIMINATION
============================================================

Cup Tournament: ELIMINATION with 4 teams, 2 games
Takım sayısı: 4
Maç sayısı: 2
✅ Maç sayısı doğru: 2

📋 İlk Tur Maçları:
   1. Beşiktaş vs Trabzonspor (ID: 1)
   2. Galatasaray vs Fenerbahçe (ID: 2)

============================================================
2️⃣ Test: 8 takım ile ELIMINATION
============================================================

Cup Tournament: ELIMINATION with 8 teams, 4 games
Takım sayısı: 8
Maç sayısı: 4
✅ Maç sayısı doğru: 4

📋 İlk Tur Maçları:
   1. Sivasspor vs Başakşehir (ID: 1)
   2. Konyaspor vs Antalyaspor (ID: 2)
   3. Beşiktaş vs Trabzonspor (ID: 3)
   4. Galatasaray vs Fenerbahçe (ID: 4)

============================================================
3️⃣ Test: 5 takım ile ELIMINATION (bye var)
============================================================
   🎫 Başakşehir has a bye (advances without playing)

Cup Tournament: ELIMINATION with 5 teams, 2 games
Takım sayısı: 5
Maç sayısı: 2
✅ Maç sayısı doğru: 2

📋 İlk Tur Maçları:
   1. Trabzonspor vs Beşiktaş (ID: 1)
   2. Galatasaray vs Fenerbahçe (ID: 2)

============================================================
4️⃣ Test: ELIMINATION2 (her eşleşme 2 maç)
============================================================

Cup Tournament: ELIMINATION2 with 4 teams, 4 games
Maç sayısı: 4
✅ Maç sayısı doğru: 4

📋 İlk Tur Maçları (rövanş dahil):
   1. Beşiktaş vs Galatasaray (ID: 1)
   2. Galatasaray vs Beşiktaş (ID: 2)
   3. Fenerbahçe vs Trabzonspor (ID: 3)
   4. Trabzonspor vs Fenerbahçe (ID: 4)

============================================================
5️⃣ Test: Rastgele eşleştirme
============================================================
Aynı takımlarla 3 farklı cup oluşturuluyor...
Cup A ilk maç: Trabzonspor vs Galatasaray
Cup B ilk maç: Fenerbahçe vs Beşiktaş
Cup C ilk maç: Beşiktaş vs Trabzonspor
✅ Rastgele eşleştirme çalışıyor!

============================================================
✅ ELIMINATION İLK TUR TESTLERİ BAŞARIYLA GEÇTİ!
============================================================

NOT: Şu an sadece ilk tur maçları oluşturuluyor.
Sonraki turlar (yarı final, final) henüz implement edilmedi.
"""""