import { useState, useRef } from 'react'
import { Outlet } from 'react-router-dom'
import { Menu, Trophy } from 'lucide-react'
import SideNav from '../SideNav'
import { useMediaQuery, mediaQueries } from '../../utils/responsive'
import { colors } from '../../styles/colors'

function Layout() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const sideNavRef = useRef(null)
  const isMobile = useMediaQuery(mediaQueries.tablet)

  const handleMobileMenuToggle = () => {
    sideNavRef.current?.toggleMobileMenu()
  }

  return (
    <div className="app-container">
      <SideNav ref={sideNavRef} onToggle={setIsSidebarCollapsed} />

      {isMobile && (
        <header className="mobile-header">
          <button
            className="mobile-header-menu-btn"
            onClick={handleMobileMenuToggle}
            aria-label="Open menu"
          >
            <Menu size={24} />
          </button>

          <div className="mobile-header-title">
            <Trophy size={24} color={colors.brand.primary} />
            <span>Sports Tracker</span>
          </div>

          <div className="mobile-header-spacer" />
        </header>
      )}

      <main className={`main-content ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Outlet />
      </main>
    </div>
  )
}

export default Layout