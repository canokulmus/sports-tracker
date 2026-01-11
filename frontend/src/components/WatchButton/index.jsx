import { Eye, EyeOff } from 'lucide-react'
import { useWatch } from '../../context/WatchContext'
import { colors } from '../../styles/colors'

function WatchButton({ gameId, isWatching: isWatchingProp, onToggle, variant = 'default', showLabel = true }) {
  const { isWatching, toggleWatch, isGameAutoWatched } = useWatch()

  const watching = isWatchingProp !== undefined ? isWatchingProp : isWatching(gameId)
  const handleToggle = onToggle || (() => toggleWatch(gameId))

  const autoWatched = gameId ? isGameAutoWatched(gameId) : false

  const handleClick = (e) => {
    e.stopPropagation()

    if (autoWatched && watching) {
      alert(`This game is automatically watched because you're watching the tournament. To unwatch this game, unwatch the tournament instead.`)
      return
    }

    handleToggle()
  }

  if (variant === 'icon-only') {
    return (
      <button
        onClick={handleClick}
        style={styles.iconButton(watching, autoWatched)}
        title={autoWatched ? 'Auto-watched from tournament' : ''}
      >
        {watching ? <Eye size={18} /> : <EyeOff size={18} />}
      </button>
    )
  }

  return (
    <button
      onClick={handleClick}
      style={styles.button(watching, autoWatched)}
      title={autoWatched ? 'Auto-watched from tournament' : ''}
    >
      {watching ? <Eye size={16} /> : <EyeOff size={16} />}
      {showLabel && <span>{watching ? (autoWatched ? 'Auto-watching' : 'Watching') : 'Watch'}</span>}
    </button>
  )
}

const styles = {
  button: (watching, autoWatched) => ({
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
    cursor: autoWatched && watching ? 'not-allowed' : 'pointer',
    opacity: autoWatched && watching ? 0.7 : 1,
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    outline: 'none',
  }),

  iconButton: (watching, autoWatched) => ({
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
    cursor: autoWatched && watching ? 'not-allowed' : 'pointer',
    opacity: autoWatched && watching ? 0.7 : 1,
    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
    outline: 'none',
  }),
}

export default WatchButton
