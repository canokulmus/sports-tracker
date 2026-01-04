import { Eye, EyeOff } from 'lucide-react'
import { useWatch } from '../../context/WatchContext'
import { colors } from '../../styles/colors'

export function WatchButton({ gameId, variant = 'default', showLabel = true }) {
  const { isWatching, toggleWatch } = useWatch()
  const watching = isWatching(gameId)

  const handleClick = (e) => {
    e.stopPropagation()
    toggleWatch(gameId)
  }

  if (variant === 'icon-only') {
    return (
      <button onClick={handleClick} style={styles.iconButton(watching)}>
        {watching ? <Eye size={18} /> : <EyeOff size={18} />}
      </button>
    )
  }

  return (
    <button onClick={handleClick} style={styles.button(watching)}>
      {watching ? <Eye size={16} /> : <EyeOff size={16} />}
      {showLabel && <span>{watching ? 'Watching' : 'Watch'}</span>}
    </button>
  )
}

const styles = {
  button: (watching) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '8px 16px',
    borderRadius: '8px',
    border: watching
      ? `1px solid ${colors.brand.primary}`
      : `1px solid ${colors.ui.border}`,
    background: watching ? `${colors.brand.primary}15` : colors.background.card,
    color: watching ? colors.brand.primary : colors.text.secondary,
    fontSize: '13px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    outline: 'none',
  }),

  iconButton: (watching) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '36px',
    height: '36px',
    borderRadius: '8px',
    border: watching
      ? `1px solid ${colors.brand.primary}`
      : `1px solid ${colors.ui.border}`,
    background: watching ? `${colors.brand.primary}15` : colors.background.card,
    color: watching ? colors.brand.primary : colors.text.secondary,
    cursor: 'pointer',
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    outline: 'none',
  }),
}
