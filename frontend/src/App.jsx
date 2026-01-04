// src/App.jsx
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

function App() {
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