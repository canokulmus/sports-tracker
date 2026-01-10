// src/components/Game/GoalDropdown.jsx
import { useState, useEffect, useRef } from 'react'
import { Target } from 'lucide-react'
import { colors } from '../../styles/colors'

function GoalDropdown({ players = [], onScore, side, disabled = false }) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelectPlayer = (playerName) => {
    onScore?.(side, playerName)
    setIsOpen(false)
  }

  if (disabled) return null

  return (
    <div style={styles.container} ref={dropdownRef} onClick={(e) => e.stopPropagation()}>
      <button
        style={styles.triggerBtn}
        onClick={(e) => {
          e.stopPropagation()
          setIsOpen(!isOpen)
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = `${colors.state.success}15`
          e.currentTarget.style.borderColor = `${colors.state.success}60`
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = colors.background.tertiary
          e.currentTarget.style.borderColor = `${colors.state.success}40`
        }}
        type="button"
      >
        <Target size={16} />
        <span>Goal</span>
      </button>

      {isOpen && (
        <div style={styles.menu}>
          <div style={styles.menuHeader}>Goal Scorer</div>

          {players.length === 0 ? (
            <div style={{ ...styles.menuItem, ...styles.menuItemDisabled }}>
              No players
            </div>
          ) : (
            players.map((player) => (
              <div
                key={player}
                style={styles.menuItem}
                onClick={() => handleSelectPlayer(player)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = colors.background.tertiary
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                }}
              >
                ⚽ {player}
              </div>
            ))
          )}

          <div style={styles.menuDivider} />
          <div
            style={styles.menuItem}
            onClick={() => handleSelectPlayer('Unknown')}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = colors.background.tertiary
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
            }}
          >
            🤷 Other / Own Goal
          </div>
        </div>
      )}
    </div>
  )
}

const styles = {
  container: {
    position: 'relative',
  },
  triggerBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    padding: '8px 16px',
    background: colors.background.tertiary,
    color: colors.state.success,
    border: `1px solid ${colors.state.success}40`,
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    outline: 'none',
  },
  menu: {
    position: 'absolute',
    top: 'calc(100% + 8px)',
    left: '50%',
    transform: 'translateX(-50%)',
    minWidth: '200px',
    background: colors.background.secondary,
    borderRadius: '12px',
    padding: '8px',
    boxShadow: `0 8px 24px rgba(0, 0, 0, 0.4), 0 0 0 1px ${colors.ui.border}`,
    zIndex: 1000,
    animation: 'slideDown 0.2s ease',
  },
  menuHeader: {
    padding: '10px 12px',
    fontSize: '12px',
    fontWeight: '700',
    color: colors.text.muted,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    borderBottom: `1px solid ${colors.ui.borderDark}`,
    marginBottom: '4px',
  },
  menuItem: {
    padding: '10px 12px',
    fontSize: '14px',
    color: colors.text.primary,
    cursor: 'pointer',
    borderRadius: '8px',
    transition: 'background 0.15s ease',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  menuItemDisabled: {
    color: colors.text.muted,
    cursor: 'not-allowed',
    opacity: 0.5,
  },
  menuDivider: {
    height: '1px',
    background: colors.ui.borderDark,
    margin: '8px 0',
  },
}

export default GoalDropdown
