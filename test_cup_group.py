# test_cup_group.py
from datetime import timedelta
from team import Team
from cup import Cup, CupType

print("=" * 60)
print("🏆 GROUP CUP TEST")
print("=" * 60)

# 16 takım oluştur (4 grup × 4 takım)
teams = [Team(f"Team {i}") for i in range(1, 17)]

# GROUP cup oluştur
cup = Cup(
    teams, 
    CupType.GROUP, 
    interval=timedelta(days=1),
    num_groups=4,      # 4 grup (A, B, C, D)
    playoff_teams=8    # 8 takım playoff'a gidecek
)

print(f"\n{cup}")

# Test 1: Gruplar oluşturuldu mu?
print("\n" + "=" * 60)
print("1️⃣ Test: Gruplar")
print("=" * 60)

print(f"\nToplam grup sayısı: {len(cup.groups)}")
assert len(cup.groups) == 4, "4 grup olmalı!"

for group_name, group_teams in cup.groups.items():
    print(f"\nGroup {group_name}: {len(group_teams)} takım")
    for team in group_teams:
        print(f"   - {team.team_name}")
    assert len(group_teams) == 4, f"Group {group_name}'de 4 takım olmalı!"

print("\n✅ Gruplar doğru oluşturuldu")

# Test 2: Her grubun maçları
print("\n" + "=" * 60)
print("2️⃣ Test: Grup maçları")
print("=" * 60)

for group_name, group_games in cup.group_games.items():
    # 4 takım → C(4,2) = 6 maç
    expected_games = 6
    print(f"\nGroup {group_name}: {len(group_games)} maç")
    assert len(group_games) == expected_games, f"Group {group_name}'de {expected_games} maç olmalı!"

print("\n✅ Grup maçları doğru")

# Test 3: Toplam maç sayısı
print("\n" + "=" * 60)
print("3️⃣ Test: Toplam maç sayısı")
print("=" * 60)

# 4 grup × 6 maç = 24 maç (grup aşaması)
expected_total = 4 * 6
print(f"\nGrup aşaması maç sayısı: {len(cup.games)}")
print(f"Beklenen: {expected_total}")
assert len(cup.games) == expected_total, f"{expected_total} maç olmalı!"

print("\n✅ Toplam maç sayısı doğru")

# Test 4: GROUP2 (çift maç)
print("\n" + "=" * 60)
print("4️⃣ Test: GROUP2 (çift maç)")
print("=" * 60)

cup2 = Cup(
    teams, 
    CupType.GROUP2, 
    interval=timedelta(days=1),
    num_groups=4,
    playoff_teams=8
)

# 4 grup × 12 maç = 48 maç
expected_double = 4 * 12
print(f"\nGRUP2 maç sayısı: {len(cup2.games)}")
print(f"Beklenen: {expected_double}")
assert len(cup2.games) == expected_double, f"{expected_double} maç olmalı!"

print("\n✅ GROUP2 doğru çalışıyor")

print("\n" + "=" * 60)
print("🎉 GROUP TEST TAMAMLANDI!")
print("=" * 60)
print("\n📌 Not: Playoff maçları henüz implement edilmedi.")
print("   Grup aşaması bittikten sonra eklenecek.")