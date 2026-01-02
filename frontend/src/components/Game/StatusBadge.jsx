// src/components/Game/StatusBadge.jsx

const STATUS_CONFIG = {
  READY: { className: 'status-ready', label: 'Bekliyor' },
  RUNNING: { className: 'status-running', label: '🔴 Canlı' },
  PAUSED: { className: 'status-paused', label: '⏸️ Duraklatıldı' },
  ENDED: { className: 'status-ended', label: 'Bitti' },
}

function StatusBadge({ state }) {
  const config = STATUS_CONFIG[state] ?? STATUS_CONFIG.READY
  
  return (
    <span className={`game-status ${config.className}`}>
      {config.label}
    </span>
  )
}

export default StatusBadge