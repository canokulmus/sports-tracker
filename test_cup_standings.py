# test_cup_standings.py
from datetime import timedelta
from team import Team
from cup import Cup, CupType
from constants import GameState

print("=" * 60)
print("📊 STANDINGS METHOD TEST (LEAGUE)")
print("=" * 60)

# 4 Takım oluştur
teams = [
    Team("Galatasaray"),
    Team("Fenerbahçe"),
    Team("Beşiktaş"),
    Team("Trabzonspor")
]

# Oyuncular ekle (skorlar için)
teams[0].addplayer("Icardi", 9)
teams[1].addplayer("Dzeko", 9)
teams[2].addplayer("Immobile", 17)
teams[3].addplayer("Trezeguet", 10)

# LEAGUE cup oluştur
cup = Cup(teams, CupType.LEAGUE, interval=timedelta(days=1))

print(f"\n{cup}")

# Test 1: Maçlar başlamadan standings
print("\n" + "=" * 60)
print("1️⃣ Test: Maçlar başlamadan standings")
print("=" * 60)

standings = cup.standings()
print(f"Standings tipi: {type(standings)}")
print(f"Takım sayısı: {len(standings)}")

print("\n📊 Puan Tablosu (maçlar başlamadan):")
print(f"{'Takım':<20} {'G':>3} {'B':>3} {'M':>3} {'A':>3} {'Y':>3} {'P':>3}")
print("-" * 60)
for team_name, won, draw, lost, gf, ga, pts in standings:
    print(f"{team_name:<20} {won:>3} {draw:>3} {lost:>3} {gf:>3} {ga:>3} {pts:>3}")

# Hiç maç oynanmadı, herkes 0 puan
for team_name, won, draw, lost, gf, ga, pts in standings:
    assert pts == 0, f"{team_name} puanı 0 olmalı!"
    assert won == 0 and draw == 0 and lost == 0, "Hiç maç oynanmadı!"
    
print("✅ Maç başlamadan standings doğru")

# Test 2: Birkaç maç oyna ve standings kontrol et
print("\n" + "=" * 60)
print("2️⃣ Test: Maçları oyna ve standings güncelle")
print("=" * 60)

# Maç 1: Galatasaray 3 - 1 Fenerbahçe
game1 = cup[1]
game1.start()
game1.score(1, teams[0], "Icardi")  # GS 1-0
game1.score(1, teams[0], "Icardi")  # GS 2-0
game1.score(1, teams[1], "Dzeko")   # GS 2-1
game1.score(1, teams[0], "Icardi")  # GS 3-1
game1.end()

print(f"✅ Maç 1 bitti: {game1.home().team_name} {game1.home_score} - {game1.away_score} {game1.away().team_name}")

# Maç 2: Galatasaray 2 - 2 Beşiktaş (Berabere)
game2 = cup[2]
game2.start()
game2.score(1, teams[0], "Icardi")    # GS 1-0
game2.score(2, teams[2], "Immobile")  # GS 1-2
game2.score(1, teams[0], "Icardi")    # GS 2-2
game2.end()

print(f"✅ Maç 2 bitti: {game2.home().team_name} {game2.home_score} - {game2.away_score} {game2.away().team_name}")

# Maç 3: Trabzonspor 0 - 2 Galatasaray
game3 = cup[3]
game3.start()
game3.score(2, teams[0], "Icardi")  # TS 0-2
game3.end()

print(f"✅ Maç 3 bitti: {game3.home().team_name} {game3.home_score} - {game3.away_score} {game3.away().team_name}")

# Standings hesapla
standings = cup.standings()

print("\n📊 Güncel Puan Tablosu:")
print(f"{'Sıra':<5} {'Takım':<20} {'G':>3} {'B':>3} {'M':>3} {'A':>3} {'Y':>3} {'AV':>4} {'P':>3}")
print("-" * 70)
for i, (team_name, won, draw, lost, gf, ga, pts) in enumerate(standings, 1):
    avg = gf - ga  # Averaj
    print(f"{i:<5} {team_name:<20} {won:>3} {draw:>3} {lost:>3} {gf:>3} {ga:>3} {avg:>+4} {pts:>3}")

# Galatasaray lider olmalı (2 galibiyet + 1 beraberlik = 5 puan)
leader = standings[0]
assert leader[0] == "Galatasaray", "Galatasaray lider olmalı!"
assert leader[6] == 5, "Galatasaray 5 puan olmalı!"  # 2+2+1 = 5
assert leader[1] == 2, "Galatasaray 2 galibiyet almalı!"  # 2 galibiyet
assert leader[2] == 1, "Galatasaray 1 beraberlik almalı!"  # 1 beraberlik

print(f"\n✅ Galatasaray lider: {leader[6]} puan")

# Test 3: Gol averajı testi
print("\n" + "=" * 60)
print("3️⃣ Test: Gol averajı sıralaması")
print("=" * 60)

# Diğer maçları oyna
# Maç 4: Fenerbahçe 5 - 0 Beşiktaş
game4 = cup[4]
game4.start()
game4.score(5, teams[1], "Dzeko")
game4.end()

# Maç 5: Fenerbahçe 3 - 0 Trabzonspor
game5 = cup[5]
game5.start()
game5.score(3, teams[1], "Dzeko")
game5.end()

# Maç 6: Beşiktaş 1 - 0 Trabzonspor
game6 = cup[6]
game6.start()
game6.score(1, teams[2], "Immobile")
game6.end()

print("✅ Tüm maçlar tamamlandı!")

# Final standings
standings = cup.standings()

print("\n📊 FİNAL PUAN TABLOSU:")
print(f"{'Sıra':<5} {'Takım':<20} {'O':>3} {'G':>3} {'B':>3} {'M':>3} {'A':>3} {'Y':>3} {'AV':>4} {'P':>3}")
print("-" * 75)
for i, (team_name, won, draw, lost, gf, ga, pts) in enumerate(standings, 1):
    played = won + draw + lost
    avg = gf - ga
    print(f"{i:<5} {team_name:<20} {played:>3} {won:>3} {draw:>3} {lost:>3} {gf:>3} {ga:>3} {avg:>+4} {pts:>3}")

# Doğrulama
print("\n🔍 Doğrulama:")
print(f"   1. {standings[0][0]} - {standings[0][6]} puan (Lider)")
print(f"   2. {standings[1][0]} - {standings[1][6]} puan")
print(f"   3. {standings[2][0]} - {standings[2][6]} puan")
print(f"   4. {standings[3][0]} - {standings[3][6]} puan (Son)")

# Lider kontrolü
assert standings[0][0] == "Galatasaray", "Lider Galatasaray olmalı!"

# Son sıra kontrolü
assert standings[3][0] == "Trabzonspor", "Trabzonspor son sırada olmalı!"

print("\n✅ Sıralama doğru!")

# Test 4: Her takımın oynadığı maç sayısı
print("\n" + "=" * 60)
print("4️⃣ Test: Her takım 3 maç oynamalı")
print("=" * 60)

for team_name, won, draw, lost, gf, ga, pts in standings:
    total_games = won + draw + lost
    print(f"   {team_name}: {total_games} maç")
    assert total_games == 3, f"{team_name} 3 maç oynamalı!"

print("✅ Her takım 3 maç oynadı")

print("\n" + "=" * 60)
print("🎉 TÜM STANDINGS TESTLERİ BAŞARIYLA GEÇTİ!")
print("=" * 60)