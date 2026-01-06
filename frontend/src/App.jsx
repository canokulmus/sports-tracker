// src/App.jsx
import { useEffect, useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import { DialogProvider } from './context/DialogContext'
import { WatchProvider } from './context/WatchContext'
import Dialog from './components/Dialog'
import Layout from './components/Layout'
import TeamsPage from './pages/TeamsPage'
import GamesPage from './pages/GamesPage'
import CupsPage from './pages/CupsPage'
import CupDetail from './pages/CupDetail'
import LivePage from './pages/LivePage'
import WatchedGamesPage from './pages/WatchedGamesPage'
import { initializeWebSocket } from './services/api'
import colors from './styles/colors'

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
    <WatchProvider>
      <DialogProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<LivePage />} />
            <Route path="teams" element={<TeamsPage />} />
            <Route path="games" element={<GamesPage />} />
            <Route path="cups" element={<CupsPage />} />
            <Route path="cups/:cupId" element={<CupDetail />} />
            <Route path="live" element={<LivePage />} />
            <Route path="watched" element={<WatchedGamesPage />} />
          </Route>
        </Routes>
        <Dialog />
      </DialogProvider>
    </WatchProvider>
  )
}

export default App