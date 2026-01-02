// src/components/Game/GoalDropdown.jsx
import { useState, useEffect, useRef } from 'react'
import { ChevronDown } from 'lucide-react'

function GoalDropdown({ players = [], onScore, side, disabled = false }) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  // Dışarı tıklayınca kapat
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
    <div className="goal-dropdown" ref={dropdownRef}>
      <button
        className="btn btn-success btn-sm"
        onClick={() => setIsOpen(!isOpen)}
        type="button"
      >
        ⚽ Gol <ChevronDown size={14} />
      </button>

      {isOpen && (
        <div className="dropdown-menu">
          <div className="dropdown-header">Gol Atan Oyuncu</div>
          
          {players.length === 0 ? (
            <div className="dropdown-item disabled">Oyuncu yok</div>
          ) : (
            players.map((player) => (
              <div
                key={player}
                className="dropdown-item"
                onClick={() => handleSelectPlayer(player)}
              >
                {player}
              </div>
            ))
          )}
          
          <div className="dropdown-divider" />
          <div
            className="dropdown-item"
            onClick={() => handleSelectPlayer('Bilinmeyen')}
          >
            Diğer / Kendi Kale
          </div>
        </div>
      )}
    </div>
  )
}

export default GoalDropdown