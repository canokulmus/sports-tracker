import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Eye, Bell, Trash2 } from 'lucide-react'
import { useWatch } from '../context/WatchContext'
import { watchApi } from '../services/api'
import { colors } from '../styles/colors'
import { useApiData } from '../hooks'
import { Loader } from '../components/Loader'
import GameCard from '../components/Game/GameCard'

function WatchedGamesPage() {
  const navigate = useNavigate()
  const { watchedGames, notifications, removeNotification, clearNotifications } = useWatch()
  const lastNotificationIdRef = useRef(null)

  const fetchWatchedGames = async () => {
    return await watchApi.getWatchedGames()
  }

  const { data: games, loading, reload } = useApiData(fetchWatchedGames, [watchedGames])

  useEffect(() => {
    if (notifications.length > 0) {
      const latestNotification = notifications[0]

      if (latestNotification.id !== lastNotificationIdRef.current) {
        lastNotificationIdRef.current = latestNotification.id
        reload()
      }
    }
  }, [notifications, reload])

  if (loading) {
    return <Loader text="Loading watched games..." />
  }

  return (
    <div>
      <div className="page-header">
        <div style={styles.titleContainer}>
          <Eye size={32} style={{ color: colors.brand.primary }} />
          <h1 className="page-title">Watched Games</h1>
        </div>
        <p className="page-subtitle">
          Games you are following for real-time updates
        </p>
      </div>

      {notifications.length > 0 && (
        <div style={styles.notificationsSection}>
          <div style={styles.notifHeader}>
            <div style={styles.notifTitle}>
              <Bell size={18} style={{ color: colors.brand.primary }} />
              <span>Recent Updates ({notifications.length})</span>
            </div>
            <button onClick={clearNotifications} style={styles.clearBtn}>
              Clear All
            </button>
          </div>

          <div style={styles.notificationsList}>
            {notifications.slice(0, 5).map((notif) => (
              <div key={notif.id} style={styles.notification}>
                <div style={styles.notifContent}>
                  <div style={styles.notifIcon}>
                    <Bell size={14} />
                  </div>
                  <div style={styles.notifText}>
                    <strong>Game #{notif.gameId}</strong> - {notif.message}
                  </div>
                  <div style={styles.notifTime}>
                    {new Date(notif.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                <button
                  onClick={() => removeNotification(notif.id)}
                  style={styles.notifClose}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={styles.statsCard}>
        <div style={styles.statsContent}>
          <div style={styles.statItem}>
            <div style={styles.statValue}>{watchedGames.length}</div>
            <div style={styles.statLabel}>Total Watched</div>
          </div>
          <div style={styles.statDivider} />
          <div style={styles.statItem}>
            <div style={styles.statValue}>
              {games?.filter(g => g.state === 'RUNNING' || g.state === 'PAUSED').length ?? 0}
            </div>
            <div style={styles.statLabel}>Live Now</div>
          </div>
          <div style={styles.statDivider} />
          <div style={styles.statItem}>
            <div style={styles.statValue}>{notifications.length}</div>
            <div style={styles.statLabel}>Notifications</div>
          </div>
        </div>
      </div>

      {!games || games.length === 0 ? (
        <div className="card" style={styles.emptyCard}>
          <div className="empty-state">
            <Eye size={64} style={{ opacity: 0.3, color: colors.text.muted }} />
            <h3 style={styles.emptyTitle}>No watched games</h3>
            <p className="text-muted">
              Click the watch button on any game to start following it
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-2">
          {games.map((game) => (
            <div key={game.id} style={styles.gameCardWrapper}>
              <GameCard
                game={game}
                variant="default"
                onClick={(gameId) => navigate(`/games/${gameId}`)}
              />
            </div>
          ))}
        </div>
      )}

      <div className="card mt-4" style={styles.footerCard}>
        <div style={styles.footerText}>
          💡 <strong>Real-time updates:</strong> You'll receive instant notifications via WebSocket when watched games are updated.
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
    padding: '24px',
    marginBottom: '24px',
    border: `1px solid ${colors.brand.primary}40`,
    boxShadow: `0 4px 16px ${colors.brand.primary}15`,
  },
  statsContent: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-around',
    gap: '24px',
  },
  statItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
  },
  statValue: {
    fontSize: '32px',
    fontWeight: '800',
    color: colors.brand.primary,
    lineHeight: '1',
  },
  statLabel: {
    fontSize: '12px',
    fontWeight: '500',
    color: colors.text.muted,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  statDivider: {
    width: '1px',
    height: '40px',
    background: colors.ui.border,
    opacity: 0.5,
  },
  notificationsSection: {
    marginBottom: '24px',
  },
  notifHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },
  notifTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '16px',
    fontWeight: '600',
    color: colors.text.primary,
  },
  clearBtn: {
    padding: '6px 12px',
    borderRadius: '6px',
    border: `1px solid ${colors.ui.border}`,
    background: colors.background.secondary,
    color: colors.text.secondary,
    fontSize: '13px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  notificationsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  notification: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    background: colors.background.secondary,
    borderRadius: '8px',
    border: `1px solid ${colors.ui.border}`,
  },
  notifContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    flex: 1,
  },
  notifIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '32px',
    height: '32px',
    borderRadius: '6px',
    background: `${colors.brand.primary}15`,
    color: colors.brand.primary,
  },
  notifText: {
    flex: 1,
    fontSize: '14px',
    color: colors.text.secondary,
  },
  notifTime: {
    fontSize: '12px',
    color: colors.text.muted,
  },
  notifClose: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '32px',
    height: '32px',
    borderRadius: '6px',
    border: 'none',
    background: 'transparent',
    color: colors.text.muted,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  gameCardWrapper: {
    position: 'relative',
  },
  unwatchBtn: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    width: '100%',
    marginTop: '12px',
    padding: '10px',
    borderRadius: '8px',
    border: `1px solid ${colors.state.danger}40`,
    background: colors.background.secondary,
    color: colors.state.danger,
    fontSize: '13px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
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

export default WatchedGamesPage
