# test_cup_league.py
from datetime import timedelta
from team import Team
from cup import Cup, CupType

print("=" * 60)
print("🏆 LEAGUE CUP TEST")
print("=" * 60)

# 4 Takım oluştur
teams = [
    Team("Galatasaray"),
    Team("Fenerbahçe"),
    Team("Beşiktaş"),
    Team("Trabzonspor")
]

# LEAGUE tipi cup oluştur
print("\n1️⃣ LEAGUE (tek maç) oluşturuluyor...")
cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))

print(f"\n{cup}")
print(f"Toplam maç sayısı: {len(cup.games)}")

# 4 takım → C(4,2) = 6 maç olmalı
# Formül: n * (n-1) / 2
expected_games = len(teams) * (len(teams) - 1) // 2
assert len(cup.games) == expected_games, f"Beklenen {expected_games}, bulunan {len(cup.games)}"
print(f"✅ Maç sayısı doğru: {expected_games}")

# Maçları listele
print("\n📋 Maçlar:")
for i, game in enumerate(cup.games, 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name} (ID: {game.id()})")

# Tarih kontrolü
print("\n📅 İlk 3 maçın tarihleri:")
for i, game in enumerate(cup.games[:3], 1):
    print(f"   {i}. {game.datetime.strftime('%Y-%m-%d %H:%M')}")

# LEAGUE2 testi
print("\n" + "=" * 60)
print("\n2️⃣ LEAGUE2 (çift maç) oluşturuluyor...")
cup2 = Cup(teams, CupType.LEAGUE2, interval=timedelta(days=1))

print(f"\n{cup2}")
print(f"Toplam maç sayısı: {len(cup2.games)}")

# 4 takım → C(4,2) * 2 = 12 maç olmalı
expected_games2 = len(teams) * (len(teams) - 1)  # Her çift 2 kez
assert len(cup2.games) == expected_games2, f"Beklenen {expected_games2}, bulunan {len(cup2.games)}"
print(f"✅ Maç sayısı doğru: {expected_games2}")

# İlk 4 maçı göster (rövanş kontrolü)
print("\n📋 İlk 4 maç (rövanş kontrolü):")
for i, game in enumerate(cup2.games[:4], 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name} (ID: {game.id()})")

# Rövanş kontrolü
game1_home = cup2.games[0].home().team_name
game1_away = cup2.games[0].away().team_name
game2_home = cup2.games[1].home().team_name
game2_away = cup2.games[1].away().team_name

assert game1_home == game2_away, "Rövanş maçı home/away yer değiştirmeli!"
assert game1_away == game2_home, "Rövanş maçı home/away yer değiştirmeli!"
print(f"\n✅ Rövanş mantığı doğru çalışıyor!")

print("\n" + "=" * 60)
print("✅ LEAGUE TİPİ BAŞARIYLA ÇALIŞIYOR!")
print("=" * 60)

# Bonus: 6 takımla test
print("\n" + "=" * 60)
print("\n3️⃣ BONUS: 6 takımla LEAGUE testi...")
teams_6 = [
    Team("Galatasaray"),
    Team("Fenerbahçe"),
    Team("Beşiktaş"),
    Team("Trabzonspor"),
    Team("Başakşehir"),
    Team("Antalyaspor")
]

cup3 = Cup(teams_6, CupType.LEAGUE, interval=timedelta(days=1))
expected_games3 = len(teams_6) * (len(teams_6) - 1) // 2
print(f"6 takım → {expected_games3} maç bekleniyor")
print(f"Oluşturulan maç sayısı: {len(cup3.games)}")
assert len(cup3.games) == expected_games3, "6 takımlı ligde maç sayısı yanlış!"
print(f"✅ 6 takımlı lig de doğru çalışıyor!")

print("\n" + "=" * 60)
print("🎉 TÜM TESTLER BAŞARIYLA GEÇTİ!")
print("=" * 60)