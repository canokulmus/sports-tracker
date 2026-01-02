// src/components/Layout/index.jsx
import { Outlet, NavLink } from 'react-router-dom'
import { Trophy, Users, Gamepad2, Award, Radio } from 'lucide-react'

function Layout() {
  const navItems = [
    { to: '/live', icon: Radio, label: 'Canlı Skorlar' },
    { to: '/teams', icon: Users, label: 'Takımlar' },
    { to: '/games', icon: Gamepad2, label: 'Maçlar' },
    { to: '/cups', icon: Award, label: 'Turnuvalar' },
  ]

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          {/* <Trophy size={28} /> */}
          <span>Sports Tracker</span>
        </div>

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
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: '#f59e0b', // Sarı = Mock mode
                }}
              />
              <span className="text-muted" style={{ fontSize: '0.75rem' }}>
                Mock Mode
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout