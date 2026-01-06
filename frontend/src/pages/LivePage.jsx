import { Radio } from 'lucide-react'
import { gameApi } from '../services/api'
import { colors } from '../styles/colors'
import { useApiData } from '../hooks'
import { Loader } from '../components/Loader'
import GameCard from '../components/Game/GameCard'

function LivePage() {
  const fetchLiveGames = async () => {
    const allGames = await gameApi.getAll()
    return allGames.filter((g) => g.state === 'RUNNING' || g.state === 'PAUSED')
  }

  const { data: games, loading } = useApiData(fetchLiveGames)

  if (loading) {
    return <Loader text="Loading live games..." />
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div style={styles.titleContainer}>
          <Radio size={32} style={{ color: colors.state.danger }} />
          <h1 className="page-title">Live Scores</h1>
        </div>
        <p className="page-subtitle">
          Track ongoing games in real-time
        </p>
      </div>

      {/* Live Stats Card */}
      <div style={styles.statsCard}>
        <div style={styles.statsContent}>
          <div style={styles.liveDot} />
          <div style={styles.statsText}>
            <strong style={styles.statsCount}>{games?.length ?? 0}</strong> live games
          </div>
        </div>
      </div>

      {/* Live Games */}
      {!games || games.length === 0 ? (
        <div className="card" style={styles.emptyCard}>
          <div className="empty-state">
            <Radio size={64} style={{ opacity: 0.3, color: colors.text.muted }} />
            <h3 style={styles.emptyTitle}>No live games right now</h3>
            <p className="text-muted">
              Games will appear here when they start
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-2">
          {games.map((game) => (
            <GameCard
              key={game.id}
              game={game}
              variant="live"
              showWatchButton={true}
            />
          ))}
        </div>
      )}

      {/* Footer Info */}
      <div className="card mt-4" style={styles.footerCard}>
        <div style={styles.footerText}>
          💡 Use the <strong>Games</strong> page to manage games.
        </div>
      </div>
    </div>
  )
}

const styles = {
  titleContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  statsCard: {
    background: colors.gradients.card,
    borderColor: colors.brand.primary,
    borderRadius: '12px',
    padding: '20px 24px',
    marginBottom: '24px',
    border: `1px solid ${colors.brand.primary}40`,
    boxShadow: `0 4px 16px ${colors.brand.primary}15`,
  },
  statsContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  liveDot: {
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    backgroundColor: colors.state.danger,
    animation: 'pulse 2s infinite',
    boxShadow: `0 0 16px ${colors.state.danger}`,
  },
  statsText: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '6px',
  },
  statsCount: {
    fontSize: '18px',
    fontWeight: '700',
    color: colors.text.primary,
  },
  statsDivider: {
    color: colors.text.muted,
    fontSize: '18px',
  },
  statsInfo: {
    color: colors.text.secondary,
    fontSize: '14px',
  },
  emptyCard: {
    padding: '60px 24px',
  },
  emptyTitle: {
    marginTop: '16px',
    marginBottom: '8px',
    color: colors.text.primary,
  },
  footerCard: {
    opacity: 0.7,
    padding: '16px 24px',
  },
  footerText: {
    textAlign: 'center',
    color: colors.text.muted,
    fontSize: '14px',
  },
}

export default LivePage
