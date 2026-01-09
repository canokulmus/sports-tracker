// src/components/Game/ScorersList.jsx
import { colors } from '../../styles/colors'

function ScorersList({ scorers = [] }) {
  if (!scorers?.length) return null

  // Helper to format time string (MM:SS.ff -> M')
  const formatMinute = (timeStr) => {
    if (!timeStr) return null
    const minutes = Math.floor(parseFloat(timeStr.split(':')[0]))
    return `${minutes}'`
  }

  return (
    <div style={styles.container}>
      {scorers.map((scorer, idx) => {
        // Support both formats: {name, goals, minutes} from backend and {player, minute} from old format
        const playerName = scorer?.name || scorer?.player || 'Unknown'
        const goals = scorer?.goals || 1
        const minutes = scorer?.minutes || [] // Array of time strings
        const singleMinute = scorer?.minute // Old format single minute

        return (
          <div key={`${playerName}-${idx}`} style={styles.scorer}>
            <span style={styles.icon}>⚽</span>
            <span style={styles.player}>{playerName}</span>
            {goals > 1 && (
              <span style={styles.goals}>×{goals}</span>
            )}
            {/* Show minutes from timeline */}
            {minutes.length > 0 && (
              <div style={styles.minutesContainer}>
                {minutes.map((timeStr, mIdx) => (
                  <span key={mIdx} style={styles.minute}>
                    {formatMinute(timeStr)}
                  </span>
                ))}
              </div>
            )}
            {/* Fallback to old format single minute */}
            {!minutes.length && singleMinute && (
              <span style={styles.minute}>{singleMinute}'</span>
            )}
          </div>
        )
      })}
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    marginTop: '8px',
  },
  scorer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    fontSize: '13px',
    color: colors.text.secondary,
    padding: '4px 8px',
    borderRadius: '6px',
    background: `${colors.state.success}15`,
    border: `1px solid ${colors.state.success}30`,
  },
  icon: {
    fontSize: '12px',
  },
  player: {
    fontWeight: '600',
    color: colors.text.primary,
  },
  goals: {
    fontSize: '11px',
    fontWeight: '700',
    color: colors.state.success,
    padding: '2px 6px',
    borderRadius: '4px',
    background: `${colors.state.success}20`,
  },
  minutesContainer: {
    display: 'flex',
    gap: '4px',
    flexWrap: 'wrap',
  },
  minute: {
    fontSize: '11px',
    color: colors.text.muted,
    fontWeight: '500',
  },
}

export default ScorersList