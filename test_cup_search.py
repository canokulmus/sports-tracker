from datetime import timedelta
from team import Team
from cup import Cup, CupType

print("=" * 60)
print("🔍 SEARCH METHOD TEST")
print("=" * 60)

# 4 Takım oluştur
teams = [
    Team("Galatasaray"),
    Team("Fenerbahçe"),
    Team("Beşiktaş"),
    Team("Trabzonspor")
]

# LEAGUE cup oluştur
cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))

print(f"\n{cup}")
print(f"Toplam maç sayısı: {len(cup.games)}")

# Test 1: Tüm maçları getir (parametre yok)
print("\n" + "=" * 60)
print("1️⃣ Test: Tüm maçlar (parametre yok)")
print("=" * 60)
all_games = cup.search()
print(f"Bulunan maç sayısı: {len(all_games)}")
assert len(all_games) == len(cup.games), "Tüm maçlar gelmeli!"
print("✅ Tüm maçlar başarıyla getirildi")

# Test 2: Belirli bir takımın maçları
print("\n" + "=" * 60)
print("2️⃣ Test: Galatasaray'ın maçları")
print("=" * 60)
gs_games = cup.search(tname="Galatasaray")
print(f"Bulunan maç sayısı: {len(gs_games)}")

for i, game in enumerate(gs_games, 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name}")

# 4 takımlı ligde her takım 3 maç oynar (diğer 3 takıma karşı)
expected_gs_games = len(teams) - 1  # 3 maç
assert len(gs_games) == expected_gs_games, f"Galatasaray {expected_gs_games} maç oynamalı!"
print(f"✅ Galatasaray'ın tüm maçları bulundu ({expected_gs_games} maç)")

# Test 3: Büyük/küçük harf duyarlılığı
print("\n" + "=" * 60)
print("3️⃣ Test: Büyük/küçük harf kontrolü")
print("=" * 60)
gs_games_lower = cup.search(tname="galatasaray")  # Küçük harf
gs_games_upper = cup.search(tname="GALATASARAY")  # Büyük harf
gs_games_mixed = cup.search(tname="GaLaTaSaRaY")  # Karışık

assert len(gs_games_lower) == expected_gs_games, "Küçük harf çalışmıyor!"
assert len(gs_games_upper) == expected_gs_games, "Büyük harf çalışmıyor!"
assert len(gs_games_mixed) == expected_gs_games, "Karışık harf çalışmıyor!"
print("✅ Büyük/küçük harf duyarlılığı doğru çalışıyor")

# Test 4: Olmayan takım
print("\n" + "=" * 60)
print("4️⃣ Test: Olmayan takım")
print("=" * 60)
no_games = cup.search(tname="Real Madrid")
print(f"Bulunan maç sayısı: {len(no_games)}")
assert len(no_games) == 0, "Olmayan takım için 0 maç dönmeli!"
print("✅ Olmayan takım için boş liste döndü")

# Test 5: Tarih aralığı
print("\n" + "=" * 60)
print("5️⃣ Test: Tarih aralığı filtresi")
print("=" * 60)

# İlk maçın tarihi
first_game_date = cup.games[0].datetime
print(f"İlk maç tarihi: {first_game_date.strftime('%Y-%m-%d %H:%M')}")

# İlk 3 günü al
start_date = first_game_date
end_date = first_game_date + timedelta(days=2)  # İlk 3 gün (0, 1, 2)

print(f"Arama aralığı: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")

date_filtered = cup.search(between=(start_date, end_date))
print(f"Bulunan maç sayısı: {len(date_filtered)}")

for i, game in enumerate(date_filtered, 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name} - {game.datetime.strftime('%Y-%m-%d')}")

# İlk 3 gün = 3 maç olmalı (günde 1 maç)
assert len(date_filtered) == 3, "İlk 3 günde 3 maç olmalı!"
print("✅ Tarih aralığı filtresi doğru çalışıyor")

# Test 6: Kombine filtre (takım + tarih)
print("\n" + "=" * 60)
print("6️⃣ Test: Kombine filtre (Galatasaray + tarih)")
print("=" * 60)

# Galatasaray'ın ilk 2 gündeki maçları
combined = cup.search(tname="Galatasaray", between=(start_date, end_date))
print(f"Bulunan maç sayısı: {len(combined)}")

for i, game in enumerate(combined, 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name} - {game.datetime.strftime('%Y-%m-%d')}")

# Galatasaray ilk 3 maçta (her birine karşı 1 maç)
# İlk 3 gün = ilk 3 maç → Galatasaray hepsinde var
assert len(combined) <= 3, "En fazla 3 maç olabilir"
assert len(combined) > 0, "En az 1 maç olmalı"
print(f"✅ Kombine filtre doğru çalışıyor ({len(combined)} maç bulundu)")

# Test 7: Fenerbahçe'nin maçları
print("\n" + "=" * 60)
print("7️⃣ Test: Fenerbahçe'nin maçları")
print("=" * 60)
fb_games = cup.search(tname="Fenerbahçe")
print(f"Bulunan maç sayısı: {len(fb_games)}")

for i, game in enumerate(fb_games, 1):
    print(f"   {i}. {game.home().team_name} vs {game.away().team_name}")

assert len(fb_games) == expected_gs_games, f"Fenerbahçe {expected_gs_games} maç oynamalı!"
print(f"✅ Fenerbahçe'nin tüm maçları bulundu ({expected_gs_games} maç)")

print("\n" + "=" * 60)
print("🎉 TÜM SEARCH TESTLERİ BAŞARIYLA GEÇTİ!")
print("=" * 60)