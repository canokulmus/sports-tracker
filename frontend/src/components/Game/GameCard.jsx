// src/components/Game/GameCard.jsx
import { Play, Pause, Square, Trash2 } from 'lucide-react'
import StatusBadge from './StatusBadge'
import ScorersList from './ScorersList'
import GoalDropdown from './GoalDropdown'

function GameCard({
  game,
  players = { home: [], away: [] },
  // Kontroller
  showControls = false,
  showDeleteButton = false,
  // Callbacks
  onStart,
  onPause,
  onResume,
  onEnd,
  onScore,
  onDelete,
  // Stil
  variant = 'default', // 'default' | 'live' | 'compact'
}) {
  // Null safety
  if (!game) {
    return (
      <div className="game-card">
        <div className="empty-state">
          <p>Maç bilgisi bulunamadı</p>
        </div>
      </div>
    )
  }

  // Destructure with defaults
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

  // Handlers with null checks
  const handleStart = () => onStart?.(id)
  const handlePause = () => onPause?.(id)
  const handleResume = () => onResume?.(id)
  const handleEnd = () => onEnd?.(id)
  const handleDelete = () => onDelete?.(id)
  const handleScore = (side, playerName) => onScore?.(id, side, playerName)

  // CSS class based on variant and state
  const cardClassName = [
    'game-card',
    isLive && variant !== 'compact' ? 'live' : '',
    variant === 'live' ? 'game-card-live' : '',
    variant === 'compact' ? 'game-card-compact' : '',
  ].filter(Boolean).join(' ')

  const cardStyle = variant === 'live' 
    ? { background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)' }
    : {}

  return (
    <div className={cardClassName} style={cardStyle}>
      {/* Header: Status & Delete */}
      <div className="flex justify-between items-center mb-4">
        <StatusBadge state={state} />
        
        <div className="flex items-center gap-2">
          <span className="text-muted text-sm">Maç #{id}</span>
          
          {showDeleteButton && onDelete && (
            <button
              className="btn btn-danger btn-sm"
              onClick={handleDelete}
              type="button"
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>
      </div>

      {/* Main: Teams & Score */}
      <div className="game-teams">
        {/* Home Team */}
        <div className="text-center" style={{ flex: 1 }}>
          <div className="team-name">{homeName}</div>
          <ScorersList scorers={homeScorers} />
          
          {showControls && isRunning && (
            <div className="mt-4">
              <GoalDropdown
                players={homePlayers}
                onScore={handleScore}
                side="home"
              />
            </div>
          )}
        </div>

        {/* Score */}
        <div className="game-score">
          {homeScore} - {awayScore}
        </div>

        {/* Away Team */}
        <div className="text-center" style={{ flex: 1 }}>
          <div className="team-name">{awayName}</div>
          <ScorersList scorers={awayScorers} />
          
          {showControls && isRunning && (
            <div className="mt-4">
              <GoalDropdown
                players={awayPlayers}
                onScore={handleScore}
                side="away"
              />
            </div>
          )}
        </div>
      </div>

      {/* Footer: Controls */}
      {showControls && (
        <div className="game-actions">
          {isReady && onStart && (
            <button className="btn btn-success" onClick={handleStart} type="button">
              <Play size={16} /> Başlat
            </button>
          )}

          {isRunning && (
            <>
              {onPause && (
                <button className="btn btn-warning" onClick={handlePause} type="button">
                  <Pause size={16} /> Duraklat
                </button>
              )}
              {onEnd && (
                <button className="btn btn-danger" onClick={handleEnd} type="button">
                  <Square size={16} /> Bitir
                </button>
              )}
            </>
          )}

          {isPaused && (
            <>
              {onResume && (
                <button className="btn btn-success" onClick={handleResume} type="button">
                  <Play size={16} /> Devam Et
                </button>
              )}
              {onEnd && (
                <button className="btn btn-danger" onClick={handleEnd} type="button">
                  <Square size={16} /> Bitir
                </button>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default GameCard