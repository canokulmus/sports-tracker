// src/App.jsx
import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { DialogProvider, useDialog } from './context/DialogContext'
import { WatchProvider } from './context/WatchContext'
import { UserProvider, useUser } from './context/UserContext'
import Dialog from './components/Dialog'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import TeamsPage from './pages/TeamsPage'
import GamesPage from './pages/GamesPage'
import GameDetail from './pages/GameDetail'
import CupsPage from './pages/CupsPage'
import CupDetail from './pages/CupDetail'
import LivePage from './pages/LivePage'
import WatchedGamesPage from './pages/WatchedGamesPage'
import WatchedCupsPage from './pages/WatchedCupsPage'
import { initializeWebSocket, setGlobalErrorHandler, removeGlobalErrorHandler } from './services/api'
import colors from './styles/colors'

// Protected Route wrapper
function ProtectedRoute({ children }) {
  const { user, isLoading } = useUser()

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: colors.background.primary,
        color: colors.text.primary
      }}>
        Loading...
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}

// Inner component that has access to Dialog context
function AppContent() {
  const { alert } = useDialog()

  useEffect(() => {
    // Set up global error handler
    setGlobalErrorHandler((error, context) => {
      console.error('[API Error]', error, context)

      // Show error popup
      alert({
        title: 'Error',
        message: error.message || 'An unexpected error occurred',
        buttonText: 'OK'
      })
    })

    // Cleanup on unmount
    return () => {
      removeGlobalErrorHandler()
    }
  }, [alert])

  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<LivePage />} />
          <Route path="teams" element={<TeamsPage />} />
          <Route path="games" element={<GamesPage />} />
          <Route path="games/:gameId" element={<GameDetail />} />
          <Route path="cups" element={<CupsPage />} />
          <Route path="cups/:cupId" element={<CupDetail />} />
          <Route path="live" element={<LivePage />} />
          <Route path="watched-games" element={<WatchedGamesPage />} />
          <Route path="watched-cups" element={<WatchedCupsPage />} />
        </Route>
      </Routes>
      <Dialog />
    </>
  )
}

function App() {
  const [wsConnected, setWsConnected] = useState(false)
  const [wsError, setWsError] = useState(null)

  useEffect(() => {
    let mounted = true

    const connectWebSocket = async () => {
      try {
        const connected = await initializeWebSocket()
        if (mounted) {
          setWsConnected(connected)
          if (!connected) {
            setWsError('Failed to connect to backend server')
          }
        }
      } catch (error) {
        if (mounted) {
          setWsError(error.message)
          setWsConnected(false)
        }
      }
    }

    connectWebSocket()

    return () => {
      mounted = false
    }
  }, [])

  if (!wsConnected) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: colors.background.primary,
        color: colors.text.primary,
        gap: '20px',
        padding: '20px',
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '48px',
          animation: 'spin 1s linear infinite'
        }}>
          🔄
        </div>
        <h2 style={{ margin: 0 }}>Connecting to Backend...</h2>
        <p style={{ color: colors.text.secondary, maxWidth: '500px' }}>
          {wsError ? (
            <>
              <span style={{ color: colors.state.danger }}>❌ Connection Failed</span>
              <br />
              {wsError}
              <br />
              <br />
              Make sure the backend server is running:
              <br />
              <code style={{
                backgroundColor: colors.background.tertiary,
                padding: '8px 12px',
                borderRadius: '4px',
                display: 'inline-block',
                marginTop: '8px'
              }}>
                python3 server.py
              </code>
            </>
          ) : (
            'Establishing WebSocket connection to ws://localhost:8888'
          )}
        </p>
      </div>
    )
  }

  return (
    <UserProvider>
      <WatchProvider>
        <DialogProvider>
          <AppContent />
        </DialogProvider>
      </WatchProvider>
    </UserProvider>
  )
}

export default App