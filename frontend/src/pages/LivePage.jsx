// src/pages/LivePage.jsx
import { useState, useEffect } from 'react'
import { Radio } from 'lucide-react'
import { gameApi } from '../services/api'
import { colors } from '../styles/colors'

// Gol Atanlar Listesi
function ScorersList({ scorers }) {
  if (!scorers || scorers.length === 0) return null

  return (
    <div className="scorers-list">
      {scorers.map((s, idx) => (
        <span key={idx} className="scorer-item">
          ⚽ {s.player} {s.minute}'
        </span>
      ))}
    </div>
  )
}

function LivePage() {
  const [games, setGames] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGames()

    // Mock: Her 3 saniyede bir yenile (WebSocket gelince kaldırılacak)
    const interval = setInterval(loadGames, 3000)
    return () => clearInterval(interval)
  }, [])

  const loadGames = async () => {
    const allGames = await gameApi.getAll()
    // Sadece aktif maçları göster (RUNNING veya PAUSED)
    const liveGames = allGames.filter(
      (g) => g.state === 'RUNNING' || g.state === 'PAUSED'
    )
    setGames(liveGames)
    setLoading(false)
  }

  if (loading) {
    return <div className="text-center text-muted">Yükleniyor...</div>
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div className="flex items-center gap-2">
          <Radio size={28} className="text-danger" />
          <h1 className="page-title">Canlı Skorlar</h1>
        </div>
        <p className="page-subtitle">
          Şu anda devam eden maçları anlık takip edin
        </p>
      </div>

      {/* Bilgi Kartı */}
      <div
        className="card mb-4"
        style={{
          background: colors.gradients.card,
          borderColor: colors.brand.primary,
        }}
      >
        <div className="flex items-center gap-4">
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              backgroundColor: colors.state.danger,
              animation: 'pulse 2s infinite',
            }}
          />
          <div>
            <strong>{games.length}</strong> canlı maç
          </div>
          <div className="text-muted">•</div>
          <div className="text-muted text-sm">
            WebSocket bağlantısı bekleniyor (Mock Mode)
          </div>
        </div>
      </div>

      {/* Canlı Maçlar */}
      {games.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <Radio size={64} style={{ opacity: 0.3 }} />
            <h3 style={{ marginTop: 16 }}>Şu anda canlı maç yok</h3>
            <p className="text-muted">
              Maçlar başladığında burada görünecek
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-2">
          {games.map((game) => (
            <div
              key={game.id}
              className="game-card live"
              style={{
                background: colors.gradients.dark,
              }}
            >
              {/* Live Badge */}
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-2">
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor:
                        game.state === 'RUNNING'
                          ? colors.gameStatus.live
                          : colors.gameStatus.paused,
                    }}
                  />
                  <span
                    className={`game-status ${
                      game.state === 'RUNNING' ? 'status-running' : 'status-paused'
                    }`}
                  >
                    {game.state === 'RUNNING' ? '🔴 CANLI' : '⏸️ DURAKLATILDI'}
                  </span>
                </div>
                <span className="text-muted text-sm">Maç #{game.id}</span>
              </div>

              {/* Skor Tablosu */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr auto 1fr',
                  alignItems: 'center',
                  gap: 20,
                  padding: '20px 0',
                }}
              >
                {/* Ev Sahibi */}
                <div className="text-center">
                  <div
                    style={{
                      fontSize: '1.5rem',
                      fontWeight: 700,
                      marginBottom: 8,
                    }}
                  >
                    {game.home.name}
                  </div>
                  <ScorersList scorers={game.scorers?.home} />
                </div>

                {/* Skor */}
                <div
                  style={{
                    fontSize: '3rem',
                    fontWeight: 800,
                    color: colors.brand.primary,
                    textShadow: `0 0 20px ${colors.brand.primary}80`,
                  }}
                >
                  {game.score.home} - {game.score.away}
                </div>

                {/* Deplasman */}
                <div className="text-center">
                  <div
                    style={{
                      fontSize: '1.5rem',
                      fontWeight: 700,
                      marginBottom: 8,
                    }}
                  >
                    {game.away.name}
                  </div>
                  <ScorersList scorers={game.scorers?.away} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Alt Bilgi */}
      <div className="card mt-4" style={{ opacity: 0.7 }}>
        <div className="text-center text-muted text-sm">
          💡 Maçları yönetmek için <strong>Maçlar</strong> sayfasını kullanın.
        </div>
      </div>

      {/* CSS */}
      <style>{`
        .scorers-list {
          margin-top: 8px;
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .scorer-item {
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  )
}

export default LivePage