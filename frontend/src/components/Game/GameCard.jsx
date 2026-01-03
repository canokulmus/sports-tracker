// src/components/Game/GameCard.jsx
import { Play, Pause, Square, Trash2, Circle } from 'lucide-react'
import StatusBadge from './StatusBadge'
import ScorersList from './ScorersList'
import GoalDropdown from './GoalDropdown'
import { colors } from '../../styles/colors'

function GameCard({
  game,
  players = { home: [], away: [] },
  showControls = false,
  showDeleteButton = false,
  onStart,
  onPause,
  onResume,
  onEnd,
  onScore,
  onDelete,
  variant = 'default',
}) {
  if (!game) {
    return (
      <div style={styles.card}>
        <div className="empty-state">
          <p>Maç bilgisi bulunamadı</p>
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

  const homeName = home?.name ?? 'Ev Sahibi'
  const awayName = away?.name ?? 'Deplasman'
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

  const handleStart = () => onStart?.(id)
  const handlePause = () => onPause?.(id)
  const handleResume = () => onResume?.(id)
  const handleEnd = () => onEnd?.(id)
  const handleDelete = () => onDelete?.(id)
  const handleScore = (side, playerName) => onScore?.(id, side, playerName)

  const cardStyle = {
    ...styles.card,
    ...(isLive && variant !== 'compact' ? styles.cardLive : {}),
    ...(variant === 'live' ? { background: colors.gradients.dark, boxShadow: `0 8px 32px ${colors.brand.primary}20` } : {}),
  }

  return (
    <div style={cardStyle} className="game-card-hover">
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
        </div>

        <div style={styles.headerRight}>
          <span style={styles.matchId}>#{id}</span>
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
      <div style={styles.scoreBoard}>
        {/* Home Team */}
        <div style={styles.team}>
          <div style={styles.teamName}>{homeName}</div>
          <div style={{
            ...styles.score,
            ...(homeScore > awayScore && isEnded ? styles.scoreWinner : {}),
          }}>
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
          <div style={styles.teamName}>{awayName}</div>
          <div style={{
            ...styles.score,
            ...(awayScore > homeScore && isEnded ? styles.scoreWinner : {}),
          }}>
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
        <div style={styles.actions}>
          {isReady && onStart && (
            <button
              className="game-action-btn game-action-start"
              onClick={handleStart}
              type="button"
            >
              <Play size={18} />
              <span>Başlat</span>
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
                  <span>Duraklat</span>
                </button>
              )}
              {onEnd && (
                <button
                  className="game-action-btn game-action-end"
                  onClick={handleEnd}
                  type="button"
                >
                  <Square size={18} />
                  <span>Bitir</span>
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
                  <span>Devam Et</span>
                </button>
              )}
              {onEnd && (
                <button
                  className="game-action-btn game-action-end"
                  onClick={handleEnd}
                  type="button"
                >
                  <Square size={18} />
                  <span>Bitir</span>
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
    alignItems: 'center',
    marginBottom: '24px',
  },
  team: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '12px',
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
}

export default GameCard
