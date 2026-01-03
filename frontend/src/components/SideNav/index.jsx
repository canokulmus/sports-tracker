// src/components/SideNav/index.jsx
import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { Trophy, Users, Gamepad2, Award, Radio, ChevronLeft, ChevronRight } from 'lucide-react'
import { colors } from '../../styles/colors'
import './SideNav.css'

function SideNav({ onToggle }) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const handleToggle = () => {
    const newState = !isCollapsed
    setIsCollapsed(newState)
    onToggle?.(newState)
  }

  const navItems = [
    { to: '/live', icon: Radio, label: 'Live Scores' },
    { to: '/teams', icon: Users, label: 'Teams' },
    { to: '/games', icon: Gamepad2, label: 'Games' },
    { to: '/cups', icon: Award, label: 'Tournaments' },
  ]

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="logo">
        <Trophy size={28} />
        {!isCollapsed && <span>Sports Tracker</span>}
      </div>

      <button
        className="toggle-btn"
        onClick={handleToggle}
        title={isCollapsed ? 'Genişlet' : 'Daralt'}
      >
        {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
      </button>

      <nav>
        <ul className="nav-menu">
          {navItems.map((item) => (
            <li key={item.to} className="nav-item">
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'active' : ''}`
                }
                title={isCollapsed ? item.label : ''}
              >
                <item.icon size={20} />
                {!isCollapsed && <span>{item.label}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="status-wrapper">
        <div className="status-card">
          <div className="status-content">
            <div
              className="status-indicator"
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: colors.connection.mock,
              }}
            />
            {!isCollapsed && (
              <span className="status-text">Mock Mode</span>
            )}
          </div>
        </div>
      </div>
    </aside>
  )
}

export default SideNav
