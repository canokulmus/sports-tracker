// src/components/Game/GameCard.jsx
import { Play, Pause, Square, Trash2, Circle } from 'lucide-react'
import StatusBadge from './StatusBadge'
import ScorersList from './ScorersList'
import GoalDropdown from './GoalDropdown'
import WatchButton from '../WatchButton'
import { colors } from '../../styles/colors'
import { useMediaQuery, mediaQueries } from '../../utils/responsive'
import { useWatch } from '../../context/WatchContext'

function GameCard({
  game,
  players = { home: [], away: [] },
  showControls = false,
  showDeleteButton = false,
  showWatchButton = false,
  onStart,
  onPause,
  onResume,
  onEnd,
  onScore,
  onDelete,
  onClick,
  variant = 'default',
}) {
  const isMobile = useMediaQuery(mediaQueries.mobile)
  const { isWatching } = useWatch()
  const watching = isWatching(game?.id)

  if (!game) {
    return (
      <div style={styles.card}>
        <div className="empty-state">
          <p>Game information not found</p>
        </div>
      </div>
    )
  }

  const {
    id = 0,
    home = {},
    away = {},
    state = 'READY',
    score = { home: 0, away: 0 },
    scorers = { home: [], away: [] },
  } = game

  const homeName = home?.name ?? 'Home'
  const awayName = away?.name ?? 'Away'
  const homeScore = score?.home ?? 0
  const awayScore = score?.away ?? 0
  const homeScorers = scorers?.home ?? []
  const awayScorers = scorers?.away ?? []
  const homePlayers = players?.home ?? []
  const awayPlayers = players?.away ?? []

  const isRunning = state === 'RUNNING'
  const isPaused = state === 'PAUSED'
  const isReady = state === 'READY'
  const isEnded = state === 'ENDED'
  const isLive = isRunning || isPaused

  const handleStart = (e) => {
    e?.stopPropagation()
    onStart?.(id)
  }
  const handlePause = (e) => {
    e?.stopPropagation()
    onPause?.(id)
  }
  const handleResume = (e) => {
    e?.stopPropagation()
    onResume?.(id)
  }
  const handleEnd = (e) => {
    e?.stopPropagation()
    onEnd?.(id)
  }
  const handleDelete = (e) => {
    e?.stopPropagation()
    onDelete?.(id)
  }
  const handleScore = (side, playerName) => onScore?.(id, side, playerName)

  const cardStyle = {
    ...styles.card,
    ...(isLive && variant !== 'compact' ? styles.cardLive : {}),
    ...(variant === 'live' ? { background: colors.gradients.dark, boxShadow: `0 8px 32px ${colors.brand.primary}20` } : {}),
    ...(isMobile ? styles.cardMobile : {}),
  }

  const scoreBoardStyle = {
    ...styles.scoreBoard,
    ...(isMobile ? styles.scoreBoardMobile : {}),
  }

  const teamNameStyle = {
    ...styles.teamName,
    ...(isMobile ? { fontSize: '16px' } : {}),
  }

  const scoreStyle = (isWinner) => ({
    ...styles.score,
    ...(isWinner && isEnded ? styles.scoreWinner : {}),
    ...(isMobile ? { fontSize: '42px', minHeight: '42px' } : {}),
  })

  const actionsStyle = {
    ...styles.actions,
    ...(isMobile ? { flexDirection: 'column' } : {}),
  }

  const cardClasses = `game-card-hover ${isLive ? 'game-card-live' : ''}`

  const handleCardClick = () => {
    if (onClick) {
      onClick(game.id)
    }
  }

  return (
    <div
      style={{
        ...cardStyle,
        ...(onClick ? { cursor: 'pointer' } : {})
      }}
      className={cardClasses}
      onClick={handleCardClick}
    >
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          {isLive && (
            <Circle
              size={8}
              fill={isRunning ? colors.state.success : colors.state.warning}
              color={isRunning ? colors.state.success : colors.state.warning}
              style={{ animation: isRunning ? 'pulse 2s infinite' : 'none' }}
            />
          )}
          <StatusBadge state={state} />
          {watching && (
            <div style={styles.watchIndicator}>
              <Circle size={6} fill={colors.brand.primary} color={colors.brand.primary} />
              <span style={styles.watchText}>Watching</span>
            </div>
          )}
        </div>

        <div style={styles.headerRight}>
          <span style={styles.matchId}>#{id}</span>
          {showWatchButton && (
            <WatchButton gameId={id} variant="icon-only" showLabel={false} />
          )}
          {showDeleteButton && onDelete && (
            <button
              className="btn btn-danger btn-sm"
              onClick={handleDelete}
              type="button"
              style={styles.deleteBtn}
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>
      </div>

      {/* Teams & Score */}
      <div style={scoreBoardStyle}>
        {/* Home Team */}
        <div style={styles.team}>
          <div style={teamNameStyle}>{homeName}</div>
          <div style={scoreStyle(homeScore > awayScore)}>
            {homeScore}
          </div>
          <ScorersList scorers={homeScorers} />

          {showControls && isRunning && (
            <div style={styles.goalBtnContainer}>
              <GoalDropdown
                players={homePlayers}
                onScore={handleScore}
                side="home"
              />
            </div>
          )}
        </div>

        {/* Separator */}
        <div style={styles.separator}>
          <div style={styles.separatorLine} />
          <span style={styles.separatorText}>VS</span>
          <div style={styles.separatorLine} />
        </div>

        {/* Away Team */}
        <div style={styles.team}>
          <div style={teamNameStyle}>{awayName}</div>
          <div style={scoreStyle(awayScore > homeScore)}>
            {awayScore}
          </div>
          <ScorersList scorers={awayScorers} />

          {showControls && isRunning && (
            <div style={styles.goalBtnContainer}>
              <GoalDropdown
                players={awayPlayers}
                onScore={handleScore}
                side="away"
              />
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      {showControls && (
        <div style={actionsStyle}>
          {isReady && onStart && (
            <button
              className="game-action-btn game-action-start"
              onClick={handleStart}
              type="button"
            >
              <Play size={18} />
              <span>Start</span>
            </button>
          )}

          {isRunning && (
            <>
              {onPause && (
                <button
                  className="game-action-btn game-action-pause"
                  onClick={handlePause}
                  type="button"
                >
                  <Pause size={18} />
                  <span>Pause</span>
                </button>
              )}
              {onEnd && (
                <button
                  className="game-action-btn game-action-end"
                  onClick={handleEnd}
                  type="button"
                >
                  <Square size={18} />
                  <span>End</span>
                </button>
              )}
            </>
          )}

          {isPaused && (
            <>
              {onResume && (
                <button
                  className="game-action-btn game-action-start"
                  onClick={handleResume}
                  type="button"
                >
                  <Play size={18} />
                  <span>Resume</span>
                </button>
              )}
              {onEnd && (
                <button
                  className="game-action-btn game-action-end"
                  onClick={handleEnd}
                  type="button"
                >
                  <Square size={18} />
                  <span>End</span>
                </button>
              )}
            </>
          )}
        </div>
      )}

      {/* Inline Styles for Subtle Dark Theme Buttons */}
      <style>{`
        .game-action-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 10px 20px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          outline: none;
          border: 1px solid;
        }

        .game-action-start {
          background: ${colors.background.tertiary};
          border-color: ${colors.state.success}40;
          color: ${colors.state.success};
        }

        .game-action-start:hover {
          background: ${colors.state.success}15;
          border-color: ${colors.state.success}60;
          transform: translateY(-1px);
        }

        .game-action-pause {
          background: ${colors.background.tertiary};
          border-color: ${colors.state.warning}40;
          color: ${colors.state.warning};
        }

        .game-action-pause:hover {
          background: ${colors.state.warning}15;
          border-color: ${colors.state.warning}60;
          transform: translateY(-1px);
        }

        .game-action-end {
          background: ${colors.background.tertiary};
          border-color: ${colors.state.danger}40;
          color: ${colors.state.danger};
        }

        .game-action-end:hover {
          background: ${colors.state.danger}15;
          border-color: ${colors.state.danger}60;
          transform: translateY(-1px);
        }

        .game-action-btn:active {
          transform: translateY(0);
        }

        /* Responsive GameCard Styles */
        @media (max-width: 480px) {
          .game-card-hover {
            padding: 16px !important;
          }

          .game-action-btn {
            flex: 1;
            width: 100%;
          }
        }
      `}</style>
    </div>
  )
}

const styles = {
  card: {
    background: colors.background.secondary,
    borderRadius: '16px',
    padding: '24px',
    border: `1px solid ${colors.ui.border}`,
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    position: 'relative',
    overflow: 'visible',
    cursor: 'pointer',
  },
  cardLive: {
    borderColor: colors.state.success,
    boxShadow: `0 0 0 1px ${colors.state.success}40, 0 8px 24px ${colors.state.success}20`,
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  watchIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '4px 10px',
    borderRadius: '12px',
    background: `${colors.brand.primary}10`,
    border: `1px solid ${colors.brand.primary}30`,
  },
  watchText: {
    fontSize: '12px',
    fontWeight: '500',
    color: colors.brand.primary,
  },
  matchId: {
    fontSize: '14px',
    color: colors.text.muted,
    fontWeight: '500',
  },
  deleteBtn: {
    padding: '6px 10px',
  },
  scoreBoard: {
    display: 'grid',
    gridTemplateColumns: '1fr auto 1fr',
    gap: '32px',
    alignItems: 'start',
    marginBottom: '24px',
  },
  team: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '12px',
    minHeight: '200px',
  },
  teamName: {
    fontSize: '20px',
    fontWeight: '700',
    color: colors.text.primary,
    textAlign: 'center',
    lineHeight: '1.2',
  },
  score: {
    fontSize: '56px',
    fontWeight: '800',
    color: colors.brand.primary,
    lineHeight: '1',
    textShadow: `0 0 12px ${colors.brand.primary}30`,
    transition: 'all 0.3s ease',
    minHeight: '56px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  scoreWinner: {
    color: colors.state.success,
    textShadow: `0 0 16px ${colors.state.success}40`,
    transform: 'scale(1.08)',
  },
  separator: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    opacity: '0.5',
  },
  separatorLine: {
    width: '1px',
    height: '40px',
    background: `linear-gradient(180deg, transparent, ${colors.ui.border}, transparent)`,
  },
  separatorText: {
    fontSize: '12px',
    fontWeight: '700',
    color: colors.text.muted,
    letterSpacing: '2px',
  },
  goalBtnContainer: {
    marginTop: '8px',
  },
  actions: {
    display: 'flex',
    gap: '12px',
    marginTop: '24px',
    paddingTop: '24px',
    borderTop: `1px solid ${colors.ui.borderDark}`,
  },
  cardMobile: {
    padding: '16px',
  },
  scoreBoardMobile: {
    gap: '16px',
  },
}

export default GameCard
