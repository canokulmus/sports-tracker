// src/components/Layout/index.jsx
import { Outlet } from 'react-router-dom'
import SideNav from '../SideNav'

function Layout() {
  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <SideNav />

      {/* Main Content */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout