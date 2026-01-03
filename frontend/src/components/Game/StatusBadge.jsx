// src/components/Game/StatusBadge.jsx
import { colors } from '../../styles/colors'

const STATUS_CONFIG = {
  READY: {
    label: 'Ready',
    color: colors.gameStatus.scheduled,
    bgColor: `${colors.gameStatus.scheduled}20`,
    icon: '⏱️',
  },
  RUNNING: {
    label: 'Live',
    color: colors.gameStatus.live,
    bgColor: `${colors.gameStatus.live}20`,
    icon: '🔴',
  },
  PAUSED: {
    label: 'Paused',
    color: colors.gameStatus.paused,
    bgColor: `${colors.gameStatus.paused}20`,
    icon: '⏸️',
  },
  ENDED: {
    label: 'Ended',
    color: colors.gameStatus.ended,
    bgColor: `${colors.gameStatus.ended}20`,
    icon: '✓',
  },
}

function StatusBadge({ state }) {
  const config = STATUS_CONFIG[state] ?? STATUS_CONFIG.READY

  const badgeStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: '6px 12px',
    borderRadius: '8px',
    fontSize: '13px',
    fontWeight: '600',
    backgroundColor: config.bgColor,
    color: config.color,
    border: `1px solid ${config.color}40`,
    transition: 'all 0.2s ease',
  }

  return (
    <span style={badgeStyle}>
      <span>{config.icon}</span>
      <span>{config.label}</span>
    </span>
  )
}

export default StatusBadge
