// src/pages/GameDetail.jsx
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Play, Pause, Square, Trophy, Clock, Calendar } from 'lucide-react'
import { gameApi, onGameNotification } from '../services/api'
import { colors } from '../styles/colors'
import { Loader } from '../components/Loader'
import StatusBadge from '../components/Game/StatusBadge'
import ScorersList from '../components/Game/ScorersList'
import GoalDropdown from '../components/Game/GoalDropdown'
import WatchButton from '../components/WatchButton'

function GameDetail() {
  const { gameId } = useParams()
  const navigate = useNavigate()
  const [game, setGame] = useState(null)
  const [players, setPlayers] = useState({ home: [], away: [] })
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadGameData()
  }, [gameId])

  // Listen for WebSocket notifications to update game data in real-time
  useEffect(() => {
    const unsubscribe = onGameNotification((notification) => {
      // Reload game data if this game was updated
      if (notification.type === 'NOTIFICATION' && notification.game_id === parseInt(gameId)) {
        console.log('[GameDetail] Received update for this game, reloading...')
        loadGameData()
      }
    })

    return () => {
      if (unsubscribe) unsubscribe()
    }
  }, [gameId])

  const loadGameData = async () => {
    try {
      setLoading(true)
      const gameData = await gameApi.getById(parseInt(gameId))
      setGame(gameData)

      // Load players
      const playersData = await gameApi.getPlayersForGame(parseInt(gameId))
      setPlayers(playersData)

      // TODO: Add getStats API call when implemented
      // For now, derive basic stats from game data
      if (gameData) {
        setStats({
          home: {
            goals: gameData.score?.home || 0,
            scorers: gameData.scorers?.home || []
          },
          away: {
            goals: gameData.score?.away || 0,
            scorers: gameData.scorers?.away || []
          }
        })
      }
    } catch (error) {
      console.error('Failed to load game data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async () => {
    await gameApi.start(parseInt(gameId))
    await loadGameData()
  }

  const handlePause = async () => {
    await gameApi.pause(parseInt(gameId))
    await loadGameData()
  }

  const handleResume = async () => {
    await gameApi.resume(parseInt(gameId))
    await loadGameData()
  }

  const handleEnd = async () => {
    await gameApi.end(parseInt(gameId))
    await loadGameData()
  }

  const handleScore = async (side, playerName) => {
    await gameApi.score(parseInt(gameId), side, playerName)
    await loadGameData()
  }

  if (loading) {
    return <Loader text="Loading game details..." />
  }

  if (!game) {
    return (
      <div style={styles.container}>
        <div className="empty-state">
          <p>Game not found</p>
        </div>
      </div>
    )
  }

  const homeName = game.home?.name ?? 'Home'
  const awayName = game.away?.name ?? 'Away'
  const homeScore = game.score?.home ?? 0
  const awayScore = game.score?.away ?? 0
  const homeScorers = game.scorers?.home ?? []
  const awayScorers = game.scorers?.away ?? []
  const isRunning = game.state === 'RUNNING'
  const isPaused = game.state === 'PAUSED'
  const isReady = game.state === 'READY'
  const isEnded = game.state === 'ENDED'
  const isLive = isRunning || isPaused

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <button
          style={styles.backButton}
          onClick={() => navigate(-1)}
          className="btn-ghost"
        >
          <ArrowLeft size={20} />
          <span>Back</span>
        </button>

        <div style={styles.headerActions}>
          <WatchButton gameId={game.id} />
        </div>
      </div>

      {/* Match Card */}
      <div className="card" style={styles.matchCard}>
        <div style={styles.matchHeader}>
          <div style={styles.matchHeaderLeft}>
            <StatusBadge state={game.state} />
            <span style={styles.matchId}>#{game.id}</span>
          </div>
          {game.datetime && (
            <div style={styles.dateTime}>
              <Calendar size={14} />
              <span>{new Date(game.datetime).toLocaleDateString()}</span>
            </div>
          )}
        </div>

        {/* Score Display */}
        <div style={styles.scoreBoard}>
          {/* Home Team */}
          <div style={styles.team}>
            <h2 style={styles.teamName}>{homeName}</h2>
            <div style={{
              ...styles.score,
              ...(homeScore > awayScore && isEnded ? styles.scoreWinner : {})
            }}>
              {homeScore}
            </div>
          </div>

          {/* VS Separator */}
          <div style={styles.separator}>
            <span style={styles.vs}>VS</span>
          </div>

          {/* Away Team */}
          <div style={styles.team}>
            <h2 style={styles.teamName}>{awayName}</h2>
            <div style={{
              ...styles.score,
              ...(awayScore > homeScore && isEnded ? styles.scoreWinner : {})
            }}>
              {awayScore}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={styles.actions}>
          {isReady && (
            <button
              className="btn btn-success"
              onClick={handleStart}
              style={styles.actionBtn}
            >
              <Play size={18} />
              Start Match
            </button>
          )}

          {isRunning && (
            <>
              <button
                className="btn btn-warning"
                onClick={handlePause}
                style={styles.actionBtn}
              >
                <Pause size={18} />
                Pause
              </button>
              <button
                className="btn btn-danger"
                onClick={handleEnd}
                style={styles.actionBtn}
              >
                <Square size={18} />
                End Match
              </button>
            </>
          )}

          {isPaused && (
            <>
              <button
                className="btn btn-success"
                onClick={handleResume}
                style={styles.actionBtn}
              >
                <Play size={18} />
                Resume
              </button>
              <button
                className="btn btn-danger"
                onClick={handleEnd}
                style={styles.actionBtn}
              >
                <Square size={18} />
                End Match
              </button>
            </>
          )}
        </div>
      </div>

      {/* Stats Section */}
      <div className="card" style={styles.statsCard}>
        <h3 className="card-title" style={styles.sectionTitle}>
          <Trophy size={20} />
          STATS
        </h3>

        <div style={styles.statsGrid}>
          {/* Home Team Stats */}
          <div style={styles.teamStats}>
            <h4 style={styles.teamStatsTitle}>{homeName}</h4>

            <div style={styles.statRow}>
              <span style={styles.statLabel}>Goals</span>
              <span style={styles.statValue}>{homeScore}</span>
            </div>

            {homeScorers.length > 0 && (
              <div style={styles.scorersSection}>
                <span style={styles.scorersLabel}>Goal Scorers</span>
                <div style={styles.scorersList}>
                  {homeScorers.map((scorer, idx) => {
                    const playerName = scorer?.name || scorer?.player || 'Unknown'
                    const goals = scorer?.goals || 1
                    const minutes = scorer?.minutes || []

                    // Helper to format time string (MM:SS.ff -> M')
                    const formatMinute = (timeStr) => {
                      if (!timeStr) return null
                      const mins = Math.floor(parseFloat(timeStr.split(':')[0]))
                      return `${mins}'`
                    }

                    return (
                      <div key={idx} style={styles.scorerItem}>
                        <span style={styles.scorerIcon}>⚽</span>
                        <span style={styles.scorerName}>{playerName}</span>
                        {goals > 1 && (
                          <span style={styles.scorerGoals}>×{goals}</span>
                        )}
                        {minutes.length > 0 && (
                          <div style={styles.minutesRow}>
                            {minutes.map((timeStr, mIdx) => (
                              <span key={mIdx} style={styles.scorerMinute}>
                                {formatMinute(timeStr)}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Score Goal Button for Running Games */}
            {isRunning && (
              <div style={styles.goalAction}>
                <GoalDropdown
                  players={players.home}
                  onScore={handleScore}
                  side="home"
                />
              </div>
            )}
          </div>

          {/* Center Divider */}
          <div style={styles.statsDivider} />

          {/* Away Team Stats */}
          <div style={styles.teamStats}>
            <h4 style={styles.teamStatsTitle}>{awayName}</h4>

            <div style={styles.statRow}>
              <span style={styles.statLabel}>Goals</span>
              <span style={styles.statValue}>{awayScore}</span>
            </div>

            {awayScorers.length > 0 && (
              <div style={styles.scorersSection}>
                <span style={styles.scorersLabel}>Goal Scorers</span>
                <div style={styles.scorersList}>
                  {awayScorers.map((scorer, idx) => {
                    const playerName = scorer?.name || scorer?.player || 'Unknown'
                    const goals = scorer?.goals || 1
                    const minutes = scorer?.minutes || []

                    // Helper to format time string (MM:SS.ff -> M')
                    const formatMinute = (timeStr) => {
                      if (!timeStr) return null
                      const mins = Math.floor(parseFloat(timeStr.split(':')[0]))
                      return `${mins}'`
                    }

                    return (
                      <div key={idx} style={styles.scorerItem}>
                        <span style={styles.scorerIcon}>⚽</span>
                        <span style={styles.scorerName}>{playerName}</span>
                        {goals > 1 && (
                          <span style={styles.scorerGoals}>×{goals}</span>
                        )}
                        {minutes.length > 0 && (
                          <div style={styles.minutesRow}>
                            {minutes.map((timeStr, mIdx) => (
                              <span key={mIdx} style={styles.scorerMinute}>
                                {formatMinute(timeStr)}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Score Goal Button for Running Games */}
            {isRunning && (
              <div style={styles.goalAction}>
                <GoalDropdown
                  players={players.away}
                  onScore={handleScore}
                  side="away"
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Match Info */}
      <div className="card" style={styles.infoCard}>
        <h3 className="card-title" style={styles.sectionTitle}>
          <Clock size={20} />
          Match Information
        </h3>

        <div style={styles.infoGrid}>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Match ID</span>
            <span style={styles.infoValue}>#{game.id}</span>
          </div>

          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Status</span>
            <StatusBadge state={game.state} />
          </div>

          {game.datetime && (
            <div style={styles.infoItem}>
              <span style={styles.infoLabel}>Date</span>
              <span style={styles.infoValue}>
                {new Date(game.datetime).toLocaleString()}
              </span>
            </div>
          )}

          {game.group && (
            <div style={styles.infoItem}>
              <span style={styles.infoLabel}>Group</span>
              <span style={styles.infoValue}>Group {game.group}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  backButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    border: 'none',
    background: 'transparent',
    color: colors.text.secondary,
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    borderRadius: '8px',
    transition: 'all 0.2s ease',
  },
  headerActions: {
    display: 'flex',
    gap: '12px',
  },
  matchCard: {
    marginBottom: '24px',
  },
  matchHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '32px',
  },
  matchHeaderLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  matchId: {
    fontSize: '14px',
    color: colors.text.muted,
    fontWeight: '500',
  },
  dateTime: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '13px',
    color: colors.text.muted,
  },
  scoreBoard: {
    display: 'grid',
    gridTemplateColumns: '1fr auto 1fr',
    gap: '48px',
    alignItems: 'center',
    marginBottom: '32px',
    padding: '32px 0',
  },
  team: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '16px',
  },
  teamName: {
    fontSize: '28px',
    fontWeight: '700',
    color: colors.text.primary,
    textAlign: 'center',
  },
  score: {
    fontSize: '72px',
    fontWeight: '800',
    color: colors.brand.primary,
    lineHeight: '1',
    textShadow: `0 0 16px ${colors.brand.primary}30`,
    transition: 'all 0.3s ease',
  },
  scoreWinner: {
    color: colors.state.success,
    textShadow: `0 0 20px ${colors.state.success}40`,
    transform: 'scale(1.1)',
  },
  separator: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  vs: {
    fontSize: '16px',
    fontWeight: '700',
    color: colors.text.muted,
    letterSpacing: '3px',
  },
  actions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
    paddingTop: '24px',
    borderTop: `1px solid ${colors.ui.borderDark}`,
  },
  actionBtn: {
    minWidth: '140px',
  },
  statsCard: {
    marginBottom: '24px',
  },
  sectionTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '24px',
    fontSize: '18px',
    fontWeight: '700',
    color: colors.brand.primary,
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr auto 1fr',
    gap: '32px',
  },
  teamStats: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  teamStatsTitle: {
    fontSize: '20px',
    fontWeight: '700',
    color: colors.text.primary,
    marginBottom: '8px',
    paddingBottom: '12px',
    borderBottom: `2px solid ${colors.ui.border}`,
  },
  statRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 0',
  },
  statLabel: {
    fontSize: '14px',
    color: colors.text.secondary,
    fontWeight: '500',
  },
  statValue: {
    fontSize: '24px',
    fontWeight: '700',
    color: colors.brand.primary,
  },
  scorersSection: {
    marginTop: '8px',
  },
  scorersLabel: {
    display: 'block',
    fontSize: '13px',
    color: colors.text.muted,
    fontWeight: '600',
    marginBottom: '12px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  scorersList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  scorerItem: {
    display: 'flex',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '8px',
    padding: '8px 12px',
    background: `${colors.state.success}10`,
    borderRadius: '8px',
    border: `1px solid ${colors.state.success}20`,
  },
  scorerIcon: {
    fontSize: '14px',
  },
  scorerName: {
    fontSize: '14px',
    fontWeight: '600',
    color: colors.text.primary,
    flex: 1,
  },
  scorerGoals: {
    fontSize: '12px',
    fontWeight: '700',
    color: colors.state.success,
    padding: '2px 8px',
    borderRadius: '6px',
    background: `${colors.state.success}20`,
  },
  minutesRow: {
    display: 'flex',
    gap: '4px',
    flexWrap: 'wrap',
  },
  scorerMinute: {
    fontSize: '11px',
    color: colors.text.muted,
    fontWeight: '500',
    padding: '2px 6px',
    borderRadius: '4px',
    background: `${colors.background.tertiary}`,
    border: `1px solid ${colors.ui.border}`,
  },
  goalAction: {
    marginTop: '16px',
    paddingTop: '16px',
    borderTop: `1px solid ${colors.ui.border}`,
  },
  statsDivider: {
    width: '2px',
    background: `linear-gradient(180deg, transparent, ${colors.ui.border}, transparent)`,
  },
  infoCard: {
    marginBottom: '24px',
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
  },
  infoItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    padding: '16px',
    background: colors.background.tertiary,
    borderRadius: '12px',
    border: `1px solid ${colors.ui.border}`,
  },
  infoLabel: {
    fontSize: '12px',
    color: colors.text.muted,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  infoValue: {
    fontSize: '16px',
    color: colors.text.primary,
    fontWeight: '600',
  },
}

export default GameDetail
