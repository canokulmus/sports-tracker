// src/components/Game/ScorersList.jsx
import { colors } from '../../styles/colors'

function ScorersList({ scorers = [] }) {
  if (!scorers?.length) return null

  return (
    <div style={styles.container}>
      {scorers.map((scorer, idx) => (
        <div key={`${scorer?.player}-${scorer?.minute}-${idx}`} style={styles.scorer}>
          <span style={styles.icon}>⚽</span>
          <span style={styles.player}>{scorer?.player ?? 'Unknown'}</span>
          {scorer?.minute && (
            <span style={styles.minute}>{scorer.minute}'</span>
          )}
        </div>
      ))}
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
  minute: {
    fontSize: '11px',
    color: colors.text.muted,
    fontWeight: '500',
  },
}

export default ScorersList