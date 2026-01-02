// src/components/SideNav/index.jsx
import { NavLink } from 'react-router-dom'
import { Trophy, Users, Gamepad2, Award, Radio } from 'lucide-react'
import { colors } from '../../styles/colors'
import './SideNav.css'

function SideNav() {
  const navItems = [
    { to: '/live', icon: Radio, label: 'Canlı Skorlar' },
    { to: '/teams', icon: Users, label: 'Takımlar' },
    { to: '/games', icon: Gamepad2, label: 'Maçlar' },
    { to: '/cups', icon: Award, label: 'Turnuvalar' },
  ]

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="logo">
        <Trophy size={28} />
        <span>Sports Tracker</span>
      </div>

      {/* Navigation Menu */}
      <nav>
        <ul className="nav-menu">
          {navItems.map((item) => (
            <li key={item.to} className="nav-item">
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `nav-link ${isActive ? 'active' : ''}`
                }
              >
                <item.icon size={20} />
                <span>{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Connection Status - Backend bağlanınca aktif olacak */}
      <div style={{ marginTop: 'auto', paddingTop: '20px' }}>
        <div className="card" style={{ padding: '12px' }}>
          <div className="flex items-center gap-2">
            <div
              className="status-indicator"
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: colors.connection.mock,
              }}
            />
            <span className="text-muted" style={{ fontSize: '0.75rem' }}>
              Mock Mode
            </span>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default SideNav
