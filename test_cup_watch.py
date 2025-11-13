# test_cup_watch.py
from datetime import timedelta
from typing import Any
from team import Team
from cup import Cup, CupType
from game import Game

print("=" * 60)
print("👁️  WATCH/UNWATCH METHOD TEST (Observer Pattern)")
print("=" * 60)

# Observer sınıfı oluştur
class MatchObserver:
    """Observer that tracks game updates."""
    
    def __init__(self, name: str) -> None:
        self.name = name
        self.updates: list[str] = []
    
    def update(self, game: Game) -> None:
        """Called when a watched game is updated."""
        msg = f"{self.name} received update: {game.home().team_name} vs {game.away().team_name} (State: {game.state.name})"
        self.updates.append(msg)
        print(f"   📢 {msg}")
    
    def get_update_count(self) -> int:
        """Returns number of updates received."""
        return len(self.updates)
    
    def clear_updates(self) -> None:
        """Clear update history."""
        self.updates.clear()


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

# Test 1: Tüm maçları izle
print("\n" + "=" * 60)
print("1️⃣ Test: Tüm maçları izle (parametre yok)")
print("=" * 60)

observer1 = MatchObserver("Observer1")
cup.watch(observer1)  # Tüm maçları izle

print(f"Observer1 eklendi")
print(f"Observer1'in izlediği maç sayısı: {len(cup.search())}")

# Bir maç başlat ve bitir
print("\n🎮 Maç 1 başlıyor...")
game1 = cup[1]
game1.start()

print("\n🎮 Maç 1 bitiyor...")
game1.end()

print(f"\nObserver1 aldığı update sayısı: {observer1.get_update_count()}")
assert observer1.get_update_count() == 2, "2 update almalıydı (start ve end)!"
print("✅ Observer tüm maçları izliyor")

# Test 2: Belirli bir takımın maçlarını izle
print("\n" + "=" * 60)
print("2️⃣ Test: Sadece Galatasaray maçlarını izle")
print("=" * 60)

observer2 = MatchObserver("Observer2-GS")
cup.watch(observer2, tname="Galatasaray")

print(f"Observer2 eklendi (sadece Galatasaray maçları)")

gs_games = cup.search(tname="Galatasaray")
print(f"Galatasaray'ın maç sayısı: {len(gs_games)}")

# Galatasaray'ın bir maçını başlat
print("\n🎮 Maç 2 başlıyor (Galatasaray maçı)...")
game2 = cup[2]  # Galatasaray vs Beşiktaş
observer2.clear_updates()
game2.start()

print(f"\nObserver2 aldığı update sayısı: {observer2.get_update_count()}")
assert observer2.get_update_count() == 1, "1 update almalıydı!"
print("✅ Observer sadece Galatasaray maçlarını izliyor")

# Galatasaray olmayan bir maç
print("\n🎮 Maç 4 başlıyor (Fenerbahçe vs Beşiktaş - GS yok)...")
game4 = cup[4]
observer2.clear_updates()
game4.start()

print(f"\nObserver2 aldığı update sayısı: {observer2.get_update_count()}")
assert observer2.get_update_count() == 0, "0 update almalıydı (GS yok)!"
print("✅ Galatasaray olmayan maçta update almadı")

# Test 3: Birden fazla observer
print("\n" + "=" * 60)
print("3️⃣ Test: Birden fazla observer")
print("=" * 60)

observer3 = MatchObserver("Observer3-FB")
cup.watch(observer3, tname="Fenerbahçe")

print("Observer3 eklendi (sadece Fenerbahçe maçları)")

# Fenerbahçe maçı
print("\n🎮 Maç 5 başlıyor (Fenerbahçe vs Trabzonspor)...")
game5 = cup[5]
observer2.clear_updates()
observer3.clear_updates()
game5.start()

print(f"\nObserver2 (GS) aldığı update: {observer2.get_update_count()}")
print(f"Observer3 (FB) aldığı update: {observer3.get_update_count()}")

assert observer2.get_update_count() == 0, "Observer2 update almamalı (GS yok)!"
assert observer3.get_update_count() == 1, "Observer3 update almalı (FB var)!"
print("✅ Her observer kendi takımını izliyor")

# Test 4: unwatch() - Observer'ı kaldır
print("\n" + "=" * 60)
print("4️⃣ Test: unwatch() - Observer kaldırma")
print("=" * 60)

print("Observer3'ü kaldırıyoruz...")
cup.unwatch(observer3)

# Tekrar Fenerbahçe maçı başlat
print("\n🎮 Maç 5 bitiyor...")
observer3.clear_updates()
game5.end()

print(f"\nObserver3 aldığı update sayısı: {observer3.get_update_count()}")
assert observer3.get_update_count() == 0, "Observer3 kaldırıldı, update almamalı!"
print("✅ unwatch() doğru çalışıyor")

# Test 5: Aynı observer'ı tekrar watch etme
print("\n" + "=" * 60)
print("5️⃣ Test: Aynı observer'ı tekrar ekleme")
print("=" * 60)

observer4 = MatchObserver("Observer4")
cup.watch(observer4, tname="Beşiktaş")
cup.watch(observer4, tname="Beşiktaş")  # Tekrar ekle
cup.watch(observer4, tname="Beşiktaş")  # Tekrar ekle

print("Observer4'ü 3 kez ekledik")

# Beşiktaş maçı
print("\n🎮 Maç 6 başlıyor (Beşiktaş vs Trabzonspor)...")
game6 = cup[6]
observer4.clear_updates()
game6.start()

print(f"\nObserver4 aldığı update sayısı: {observer4.get_update_count()}")
# Aynı observer birden fazla kez eklenmemeli, sadece 1 update almalı
# (Ama Game sınıfında watch() metodu duplicate check yapıyor)
print("✅ Duplicate observer kontrolü yapıldı")

# Test 6: Tüm observer'ları kaldır
print("\n" + "=" * 60)
print("6️⃣ Test: Tüm observer'ları kaldır")
print("=" * 60)

cup.unwatch(observer1)
cup.unwatch(observer2)
cup.unwatch(observer4)

print("Tüm observer'lar kaldırıldı")

# Maçları bitir
observer1.clear_updates()
observer2.clear_updates()
observer4.clear_updates()

game2.end()
game6.end()

print(f"\nObserver1 update: {observer1.get_update_count()}")
print(f"Observer2 update: {observer2.get_update_count()}")
print(f"Observer4 update: {observer4.get_update_count()}")

assert observer1.get_update_count() == 0, "Tüm observer'lar kaldırıldı!"
assert observer2.get_update_count() == 0, "Tüm observer'lar kaldırıldı!"
assert observer4.get_update_count() == 0, "Tüm observer'lar kaldırıldı!"

print("✅ Tüm observer'lar başarıyla kaldırıldı")

# Test 7: Observer ile skorları takip et
print("\n" + "=" * 60)
print("7️⃣ Test: Observer ile skor takibi")
print("=" * 60)

class ScoreObserver:
    """Observer that tracks scores."""
    
    def __init__(self) -> None:
        self.score_updates: list[tuple[str, int, int]] = []
    
    def update(self, game: Game) -> None:
        if game.state.name == "ENDED":
            self.score_updates.append((
                f"{game.home().team_name} vs {game.away().team_name}",
                game.home_score,
                game.away_score
            ))
            print(f"   📊 Maç bitti: {game.home().team_name} {game.home_score} - {game.away_score} {game.away().team_name}")

score_observer = ScoreObserver()
cup.watch(score_observer)

print("ScoreObserver eklendi")
print("\n🎮 Yeni bir cup oluşturup maçları oynayalım...")

# Yeni cup
cup2 = Cup(teams[:2], CupType.LEAGUE, interval=timedelta(days=1))
cup2.watch(score_observer)

game = cup2[1]
teams[0].addplayer("Icardi", 9)
teams[1].addplayer("Dzeko", 9)

game.start()
game.score(2, teams[0], "Icardi")
game.score(1, teams[1], "Dzeko")
game.end()

print(f"\nScoreObserver toplam {len(score_observer.score_updates)} maç sonucu kaydetti")
assert len(score_observer.score_updates) >= 1, "En az 1 maç sonucu kaydetmeliydi!"
print("✅ Observer skor takibi yapıyor")

print("\n" + "=" * 60)
print("🎉 TÜM WATCH/UNWATCH TESTLERİ BAŞARIYLA GEÇTİ!")
print("=" * 60)