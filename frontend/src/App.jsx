// src/App.jsx
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import TeamsPage from './pages/TeamsPage'
import GamesPage from './pages/GamesPage'
import CupsPage from './pages/CupsPage'
import LivePage from './pages/LivePage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<LivePage />} />
        <Route path="teams" element={<TeamsPage />} />
        <Route path="games" element={<GamesPage />} />
        <Route path="cups" element={<CupsPage />} />
        <Route path="live" element={<LivePage />} />
      </Route>
    </Routes>
  )
}

export default App