// src/components/Layout/index.jsx
import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import SideNav from '../SideNav'

function Layout() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  return (
    <div className="app-container">
      <SideNav onToggle={setIsSidebarCollapsed} />

      <main className={`main-content ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Outlet />
      </main>
    </div>
  )
}

export default Layout