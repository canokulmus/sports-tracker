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
    <div style={styles.container} ref={dropdownRef}>
      <button
        style={styles.triggerBtn}
        onClick={() => setIsOpen(!isOpen)}
        type="button"
      >
        <Target size={16} />
        <span>Gol</span>
      </button>

      {isOpen && (
        <div style={styles.menu}>
          <div style={styles.menuHeader}>Gol Atan Oyuncu</div>

          {players.length === 0 ? (
            <div style={{ ...styles.menuItem, ...styles.menuItemDisabled }}>
              Oyuncu yok
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
            onClick={() => handleSelectPlayer('Bilinmeyen')}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = colors.background.tertiary
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
            }}
          >
            🤷 Diğer / Kendi Kale
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
    background: colors.gradients.success,
    color: '#fff',
    border: 'none',
    borderRadius: '10px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    boxShadow: '0 2px 8px rgba(34, 197, 94, 0.25)',
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
