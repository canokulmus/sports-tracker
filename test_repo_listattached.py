# test_repo_listattached.py
from datetime import datetime, timedelta
from team import Team
from repo import Repo

print("=" * 60)
print("📋 REPO.LISTATTACHED() TEST")
print("=" * 60)

# Repo oluştur
repo = Repo()

# Objeler oluştur
print("\n1️⃣ Objeler oluşturuluyor...")
team1_id = repo.create(type="team", name="Galatasaray")
team2_id = repo.create(type="team", name="Fenerbahçe")
team3_id = repo.create(type="team", name="Beşiktaş")

print(f"   Team 1 ID: {team1_id}")
print(f"   Team 2 ID: {team2_id}")
print(f"   Team 3 ID: {team3_id}")

# Kullanıcı 1: 2 obje attach eder
print("\n2️⃣ User1: 2 obje attach ediyor...")
repo.attach(team1_id, "User1")
repo.attach(team2_id, "User1")

user1_objects = repo.listattached("User1")
print(f"\nUser1'in attach ettiği objeler: {len(user1_objects)}")
for obj_id, description in user1_objects:
    print(f"   ID {obj_id}: {description}")

assert len(user1_objects) == 2, "User1 2 obje attach etti!"
print("✅ User1 attached list doğru")

# Kullanıcı 2: 1 obje attach eder
print("\n3️⃣ User2: 1 obje attach ediyor...")
repo.attach(team3_id, "User2")

user2_objects = repo.listattached("User2")
print(f"\nUser2'nin attach ettiği objeler: {len(user2_objects)}")
for obj_id, description in user2_objects:
    print(f"   ID {obj_id}: {description}")

assert len(user2_objects) == 1, "User2 1 obje attach etti!"
print("✅ User2 attached list doğru")

# Aynı objeye iki kullanıcı attach olabilir
print("\n4️⃣ User2, Team1'e de attach oluyor...")
repo.attach(team1_id, "User2")

user1_objects = repo.listattached("User1")
user2_objects = repo.listattached("User2")

print(f"\nUser1: {len(user1_objects)} obje")
print(f"User2: {len(user2_objects)} obje")

assert len(user1_objects) == 2, "User1 hala 2 obje"
assert len(user2_objects) == 2, "User2 şimdi 2 obje"
print("✅ Çoklu kullanıcı attach çalışıyor")

# Detach sonrası
print("\n5️⃣ User1, Team1'i detach ediyor...")
repo.detach(team1_id, "User1")

user1_objects = repo.listattached("User1")
print(f"\nUser1'in kalan objeleri: {len(user1_objects)}")
for obj_id, description in user1_objects:
    print(f"   ID {obj_id}: {description}")

assert len(user1_objects) == 1, "User1'de 1 obje kalmalı!"
print("✅ Detach sonrası list doğru")

# Hiç attach etmeyen kullanıcı
print("\n6️⃣ Hiç attach etmeyen kullanıcı...")
user3_objects = repo.listattached("User3")
print(f"User3'ün objeleri: {len(user3_objects)}")

assert len(user3_objects) == 0, "User3 hiçbir şey attach etmedi!"
print("✅ Boş liste doğru")

# Tüm objeler listesi ile karşılaştırma
print("\n7️⃣ repo.list() ile karşılaştırma...")
all_objects = repo.list()
print(f"\nToplam objeler: {len(all_objects)}")
print(f"User1 attached: {len(repo.listattached('User1'))}")
print(f"User2 attached: {len(repo.listattached('User2'))}")

print("\n" + "=" * 60)
print("🎉 TÜM LISTATTACHED TESTLERİ GEÇTİ!")
print("=" * 60)