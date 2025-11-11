# test_game_stats.py

from datetime import datetime
from time import sleep
from team import Team
from game import Game

def test_game_stats():
    """Stats fonksiyonunu test et - gerçekçi maç senaryosu"""
    
    print("=" * 60)
    print("🏀 GAME STATS TEST SENARYOSU")
    print("=" * 60)
    
    # 1️⃣ Takımları oluştur
    print("\n1️⃣ Takımlar oluşturuluyor...")
    fenerbahce = Team("Fenerbahçe Beko")
    efes = Team("Anadolu Efes")
    
    # 2️⃣ Oyuncuları ekle
    print("\n2️⃣ Oyuncular ekleniyor...")
    
    # Fenerbahçe kadrosu
    fenerbahce.addplayer("Scottie Wilbekin", 0)
    fenerbahce.addplayer("Marko Guduric", 23)
    fenerbahce.addplayer("Nigel Hayes", 5)
    
    # Efes kadrosu
    efes.addplayer("Shane Larkin", 0)
    efes.addplayer("Vasilije Micic", 22)
    efes.addplayer("Bryant Dunston", 42)
    
    print(f"   {fenerbahce.team_name}: {len(fenerbahce.players)} oyuncu")
    print(f"   {efes.team_name}: {len(efes.players)} oyuncu")
    
    # 3️⃣ Maçı oluştur
    print("\n3️⃣ Maç oluşturuluyor...")
    game = Game(
        home=fenerbahce,
        away=efes,
        id_=1,
        datetime=datetime.now()
    )
    print(f"   {game}")
    
    # 4️⃣ Maç başlamadan stats
    print("\n4️⃣ Maç başlamadan STATS:")
    print("-" * 60)
    stats = game.stats()
    print(f"   Time: {stats['Time']}")
    print(f"   Home Score: {stats['Home']['Pts']}")
    print(f"   Away Score: {stats['Away']['Pts']}")
    print(f"   Timeline: {stats['Timeline']}")
    
    # 5️⃣ Maçı başlat
    print("\n5️⃣ Maç başlıyor...")
    game.start()
    print(f"   State: {game.state.name}")
    
    # 6️⃣ İlk sayılar (0-5 saniye arası)
    print("\n6️⃣ İlk çeyrek başladı...")
    
    sleep(2.5)  # 2.5 saniye
    game.score(3, efes, "Shane Larkin")
    print(f"   ⚡ Larkin 3 sayı attı!")
    
    sleep(1.8)  # 4.3 saniye toplamda
    game.score(2, fenerbahce, "Scottie Wilbekin")
    print(f"   ⚡ Wilbekin 2 sayı attı!")
    
    sleep(2.2)  # 6.5 saniye toplamda
    game.score(3, fenerbahce, "Marko Guduric")
    print(f"   ⚡ Guduric 3 sayı attı!")
    
    # 7️⃣ PAUSE sonrası stats
    print("\n7️⃣ Mola zamanı - Maç durduruluyor...")
    game.pause()
    print(f"   State: {game.state.name}")
    
    print("\n📊 PAUSE SIRASINDA STATS:")
    print("-" * 60)
    stats = game.stats()
    print(f"   Time: {stats['Time']}")
    print(f"   Score: {stats['Home']['Name']} {stats['Home']['Pts']} - {stats['Away']['Pts']} {stats['Away']['Name']}")
    print(f"\n   Home Players:")
    for player, score in stats['Home']['Players'].items():
        if score > 0:
            print(f"      {player}: {score} pts")
    print(f"\n   Away Players:")
    for player, score in stats['Away']['Players'].items():
        if score > 0:
            print(f"      {player}: {score} pts")
    print(f"\n   Timeline:")
    for time, team, player, points in stats['Timeline']:
        print(f"      {time} - {team} - {player}: {points} pts")
    
    # 8️⃣ Mola (3 saniye)
    print("\n8️⃣ Mola devam ediyor (3 saniye)...")
    sleep(3)
    print("   (Bu süre maç süresine eklenmeyecek!)")
    
    # 9️⃣ RESUME
    print("\n9️⃣ Maç devam ediyor...")
    game.resume()
    print(f"   State: {game.state.name}")
    
    # 🔟 Daha fazla sayı
    sleep(1.5)  # 8 saniye toplamda (pause dahil değil)
    game.score(2, efes, "Vasilije Micic")
    print(f"   ⚡ Micic 2 sayı attı!")
    
    sleep(2.0)  # 10 saniye toplamda
    game.score(3, fenerbahce, "Nigel Hayes")
    print(f"   ⚡ Hayes 3 sayı attı!")
    
    sleep(1.5)  # 11.5 saniye toplamda
    game.score(2, efes, "Shane Larkin")
    print(f"   ⚡ Larkin tekrar 2 sayı attı!")
    
    # 1️⃣1️⃣ RUNNING durumunda stats
    print("\n1️⃣1️⃣ Maç devam ederken STATS:")
    print("-" * 60)
    stats = game.stats()
    print(f"   Time: {stats['Time']}")
    print(f"   Score: {stats['Home']['Name']} {stats['Home']['Pts']} - {stats['Away']['Pts']} {stats['Away']['Name']}")
    print(f"\n   Home Players:")
    for player, score in stats['Home']['Players'].items():
        if score > 0:
            print(f"      {player}: {score} pts")
    print(f"\n   Away Players:")
    for player, score in stats['Away']['Players'].items():
        if score > 0:
            print(f"      {player}: {score} pts")
    print(f"\n   Timeline (son 3 olay):")
    for time, team, player, points in stats['Timeline'][-3:]:
        print(f"      {time} - {team} - {player}: {points} pts")
    
    # 1️⃣2️⃣ Maçı bitir
    print("\n1️⃣2️⃣ Maç bitiyor...")
    game.end()
    print(f"   State: {game.state.name}")
    
    # 1️⃣3️⃣ ENDED durumunda FINAL STATS
    print("\n" + "=" * 60)
    print("📊 FİNAL STATS (MAÇTAN SONRA)")
    print("=" * 60)
    stats = game.stats()
    
    print(f"\n⏱️  Time: {stats['Time']}")
    print(f"\n🏆 Final Score:")
    print(f"   {stats['Home']['Name']}: {stats['Home']['Pts']}")
    print(f"   {stats['Away']['Name']}: {stats['Away']['Pts']}")
    
    # Kazanan
    if stats['Home']['Pts'] > stats['Away']['Pts']:
        print(f"\n   🎉 {stats['Home']['Name']} KAZANDI!")
    elif stats['Away']['Pts'] > stats['Home']['Pts']:
        print(f"\n   🎉 {stats['Away']['Name']} KAZANDI!")
    else:
        print(f"\n   🤝 BERABERE!")
    
    print(f"\n📊 Player Stats:")
    print(f"\n   {stats['Home']['Name']}:")
    for player, score in stats['Home']['Players'].items():
        print(f"      #{fenerbahce.players[player]['no']:2d} {player:20s}: {score} pts")
    
    print(f"\n   {stats['Away']['Name']}:")
    for player, score in stats['Away']['Players'].items():
        print(f"      #{efes.players[player]['no']:2d} {player:20s}: {score} pts")
    
    print(f"\n⏰ Timeline (Tüm Olaylar):")
    for time, team, player, points in stats['Timeline']:
        team_emoji = "🏠" if team == "Home" else "✈️"
        print(f"      {time} {team_emoji} {player}: {points} pts")
    
    print("\n" + "=" * 60)
    print("✅ TEST TAMAMLANDI!")
    print("=" * 60)
    
    # 1️⃣4️⃣ Assertions (Doğrulama)
    print("\n1️⃣4️⃣ Doğrulama testleri...")
    
    # Toplam skor kontrolü
    assert stats['Home']['Pts'] == 8, f"Home score yanlış! Beklenen: 8, Bulunan: {stats['Home']['Pts']}"
    assert stats['Away']['Pts'] == 7, f"Away score yanlış! Beklenen: 7, Bulunan: {stats['Away']['Pts']}"
    
    # Timeline kontrolü
    assert len(stats['Timeline']) == 6, f"Timeline uzunluğu yanlış! Beklenen: 6, Bulunan: {len(stats['Timeline'])}"
    
    # Oyuncu skorları kontrolü
    assert stats['Home']['Players']['Scottie Wilbekin'] == 2, "Wilbekin skoru yanlış!"
    assert stats['Home']['Players']['Marko Guduric'] == 3, "Guduric skoru yanlış!"
    assert stats['Home']['Players']['Nigel Hayes'] == 3, "Hayes skoru yanlış!"
    assert stats['Away']['Players']['Shane Larkin'] == 5, "Larkin skoru yanlış!"  # 3 + 2
    assert stats['Away']['Players']['Vasilije Micic'] == 2, "Micic skoru yanlış!"
    
    # Time kontrolü
    assert stats['Time'] == "Full Time", f"Time yanlış! Beklenen: 'Full Time', Bulunan: {stats['Time']}"
    
    print("   ✅ Tüm skorlar doğru!")
    print("   ✅ Timeline doğru!")
    print("   ✅ Time display doğru!")
    print("   ✅ Oyuncu skorları doğru!")
    
    print("\n🎉 TÜM TESTLER BAŞARIYLA GEÇTİ!")


if __name__ == "__main__":
    test_game_stats()