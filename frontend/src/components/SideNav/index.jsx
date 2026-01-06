// src/components/SideNav/index.jsx
import { useState, useEffect, forwardRef, useImperativeHandle } from 'react'
import { NavLink } from 'react-router-dom'
import { Trophy, Users, Gamepad2, Award, Radio, Eye, ChevronLeft, ChevronRight, X } from 'lucide-react'
import { colors } from '../../styles/colors'
import { useMediaQuery, mediaQueries } from '../../utils/responsive'
import { useWatch } from '../../context/WatchContext'
import { isWebSocketConnected } from '../../services/api'
import './SideNav.css'

const SideNav = forwardRef(({ onToggle }, ref) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)
  const isMobile = useMediaQuery(mediaQueries.tablet)

  // Check WebSocket connection status
  useEffect(() => {
    const checkConnection = () => {
      setWsConnected(isWebSocketConnected())
    }

    checkConnection()
    const interval = setInterval(checkConnection, 2000)

    return () => clearInterval(interval)
  }, [])

  // Auto-close mobile menu when screen becomes larger
  useEffect(() => {
    if (!isMobile) {
      setIsMobileMenuOpen(false)
    }
  }, [isMobile])

  const handleToggle = () => {
    if (isMobile) {
      setIsMobileMenuOpen(!isMobileMenuOpen)
    } else {
      const newState = !isCollapsed
      setIsCollapsed(newState)
      onToggle?.(newState)
    }
  }

  const handleMobileMenuClose = () => {
    setIsMobileMenuOpen(false)
  }

  // Expose toggle function to parent via ref
  useImperativeHandle(ref, () => ({
    toggleMobileMenu: () => {
      if (isMobile) {
        setIsMobileMenuOpen(!isMobileMenuOpen)
      }
    }
  }))

  const { watchedGames } = useWatch()

  const navItems = [
    { to: '/live', icon: Radio, label: 'Live Scores' },
    { to: '/watched', icon: Eye, label: 'Watched', badge: watchedGames.length },
    { to: '/teams', icon: Users, label: 'Teams' },
    { to: '/games', icon: Gamepad2, label: 'Games' },
    { to: '/cups', icon: Award, label: 'Tournaments' },
  ]

  return (
    <>
      {/* Mobile backdrop */}
      {isMobile && isMobileMenuOpen && (
        <div className="sidebar-backdrop" onClick={handleMobileMenuClose} />
      )}

      <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''} ${isMobile && isMobileMenuOpen ? 'mobile-open' : ''}`}>
        {/* Mobile close button */}
        {isMobile && isMobileMenuOpen && (
          <button
            className="mobile-close-btn"
            onClick={handleMobileMenuClose}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        )}

        <div className="logo">
          <Trophy size={28} />
          {!isCollapsed && <span>Sports Tracker</span>}
        </div>

        {/* Desktop collapse button */}
        {!isMobile && (
          <button
            className="toggle-btn"
            onClick={handleToggle}
            title={isCollapsed ? 'Genişlet' : 'Daralt'}
          >
            {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </button>
        )}

        <nav>
          <ul className="nav-menu">
            {navItems.map((item) => (
              <li key={item.to} className="nav-item">
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    `nav-link ${isActive ? 'active' : ''}`
                  }
                  title={isCollapsed && !isMobile ? item.label : ''}
                  onClick={isMobile ? handleMobileMenuClose : undefined}
                >
                  <item.icon size={20} />
                  {(!isCollapsed || isMobile) && <span>{item.label}</span>}
                  {item.badge > 0 && (
                    <span className="nav-badge">{item.badge}</span>
                  )}
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
                  backgroundColor: wsConnected ? colors.state.success : colors.state.danger,
                  animation: wsConnected ? 'pulse 2s ease-in-out infinite' : 'none',
                }}
              />
              {(!isCollapsed || isMobile) && (
                <span className="status-text">
                  {wsConnected ? 'Live' : 'Disconnected'}
                </span>
              )}
            </div>
          </div>
        </div>
      </aside>
    </>
  )
})

SideNav.displayName = 'SideNav'

export default SideNav
