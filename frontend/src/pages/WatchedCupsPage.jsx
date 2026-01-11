import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trophy, Eye, Calendar, Users } from 'lucide-react'
import { watchApi, onGameNotification } from '../services/api'
import { useWatch } from '../context/WatchContext'
import { colors } from '../styles/colors'
import { Loader } from '../components/Loader'

function WatchedCupsPage() {
  const navigate = useNavigate()
  const { watchedCups, notifications, clearNotifications, removeNotification } = useWatch()
  const [cups, setCups] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadWatchedCups()
  }, [watchedCups])

  useEffect(() => {
    const unsubscribe = onGameNotification((notification) => {
      if (notification.type === 'NOTIFICATION') {
        console.log('[WatchedCupsPage] Received notification, reloading cups')
        loadWatchedCups()
      }
    })

    return () => {
      if (unsubscribe) unsubscribe()
    }
  }, [])

  const loadWatchedCups = async () => {
    try {
      setLoading(true)
      const watchedCupsData = await watchApi.getWatchedCups()
      setCups(watchedCupsData)
    } catch (error) {
      console.error('Error loading watched cups:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Loader text="Loading watched tournaments..." />
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Watched Tournaments</h1>
          <p className="page-subtitle">
            Tournaments you're following ({cups.length})
          </p>
        </div>
      </div>

      <div className="grid grid-2">
        <div>
          <div className="card">
            <h3 className="card-title mb-4">Your Watched Tournaments</h3>

            {cups.length === 0 ? (
              <div style={styles.empty}>
                <Eye size={48} color={colors.text.muted} style={{ opacity: 0.3 }} />
                <p className="text-muted">You're not watching any tournaments yet</p>
                <button
                  className="btn btn-primary"
                  onClick={() => navigate('/cups')}
                  style={{ marginTop: '16px' }}
                >
                  Browse Tournaments
                </button>
              </div>
            ) : (
              <div style={styles.cupsList}>
                {cups.map((cup) => (
                  <div
                    key={cup.id}
                    style={styles.cupCard}
                    onClick={() => navigate(`/cups/${cup.id}`)}
                  >
                    <div style={styles.cupHeader}>
                      <div style={styles.cupTitleRow}>
                        <Trophy size={20} color={getTournamentColor(cup.type)} />
                        <h4 style={styles.cupName}>{cup.name}</h4>
                      </div>
                      <span
                        className="badge"
                        style={{
                          backgroundColor: getTournamentColor(cup.type),
                          color: colors.quickColors.white,
                          fontSize: '11px',
                        }}
                      >
                        {cup.type}
                      </span>
                    </div>

                    <div style={styles.cupStats}>
                      <div style={styles.stat}>
                        <Users size={14} color={colors.text.muted} />
                        <span className="text-muted" style={{ fontSize: '13px' }}>
                          {cup.teams?.length || 0} teams
                        </span>
                      </div>
                      <div style={styles.stat}>
                        <Calendar size={14} color={colors.text.muted} />
                        <span className="text-muted" style={{ fontSize: '13px' }}>
                          {cup.gameCount || 0} games
                        </span>
                      </div>
                    </div>

                    {cup.runningGames > 0 && (
                      <div style={styles.liveIndicator}>
                        <div style={styles.liveDot} />
                        <span style={styles.liveText}>
                          {cup.runningGames} game{cup.runningGames > 1 ? 's' : ''} live
                        </span>
                      </div>
                    )}

                    <div style={styles.progress}>
                      <div style={styles.progressBar}>
                        <div
                          style={{
                            ...styles.progressFill,
                            width: `${(cup.endedGames / cup.gameCount) * 100}%`,
                          }}
                        />
                      </div>
                      <span className="text-muted" style={{ fontSize: '12px' }}>
                        {cup.endedGames}/{cup.gameCount} completed
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="card">
            <div style={styles.notifHeader}>
              <h3 className="card-title" style={{ marginBottom: 0 }}>
                Recent Updates
              </h3>
              {notifications.length > 0 && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={clearNotifications}
                >
                  Clear All
                </button>
              )}
            </div>

            {notifications.length === 0 ? (
              <div style={styles.empty}>
                <p className="text-muted">No recent updates</p>
              </div>
            ) : (
              <div style={styles.notificationsList}>
                {notifications.map((notif) => (
                  <div key={notif.id} style={styles.notification}>
                    <div style={styles.notifContent}>
                      <p style={styles.notifMessage}>{notif.message}</p>
                      <span style={styles.notifTime}>
                        {new Date(notif.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        removeNotification(notif.id)
                      }}
                      style={styles.removeBtn}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function getTournamentColor(type) {
  const colorMap = {
    LEAGUE: colors.tournament.league,
    LEAGUE2: colors.tournament.league,
    ELIMINATION: colors.tournament.elimination,
    ELIMINATION2: colors.tournament.elimination,
    GROUP: colors.tournament.group,
    GROUP2: colors.tournament.group,
  }
  return colorMap[type] || colors.text.muted
}

const styles = {
  empty: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '48px 24px',
    gap: '12px',
  },
  cupsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  cupCard: {
    padding: '16px',
    backgroundColor: colors.background.secondary,
    borderRadius: '8px',
    border: `1px solid ${colors.ui.borderSubtle}`,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  cupHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '12px',
  },
  cupTitleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flex: 1,
  },
  cupName: {
    margin: 0,
    fontSize: '16px',
    fontWeight: '600',
    color: colors.text.primary,
  },
  cupStats: {
    display: 'flex',
    gap: '16px',
    marginBottom: '12px',
  },
  stat: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  liveIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    marginBottom: '12px',
    padding: '6px 12px',
    borderRadius: '4px',
    width: 'fit-content',
  },
  liveDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: colors.state.success,
    animation: 'pulse 2s infinite',
  },
  liveText: {
    fontSize: '12px',
    fontWeight: '600',
    color: colors.state.success,
  },
  progress: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  progressBar: {
    width: '100%',
    height: '6px',
    backgroundColor: colors.background.tertiary,
    borderRadius: '3px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.brand.primary,
    transition: 'width 0.3s ease',
  },
  notifHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
  },
  notificationsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    maxHeight: '600px',
    overflowY: 'auto',
  },
  notification: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    padding: '12px',
    backgroundColor: colors.background.secondary,
    borderRadius: '6px',
    border: `1px solid ${colors.ui.borderSubtle}`,
  },
  notifContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  notifMessage: {
    margin: 0,
    fontSize: '14px',
    color: colors.text.primary,
  },
  notifTime: {
    fontSize: '12px',
    color: colors.text.muted,
  },
  removeBtn: {
    padding: '2px 8px',
    fontSize: '18px',
    lineHeight: '1',
  },
}

export default WatchedCupsPage
