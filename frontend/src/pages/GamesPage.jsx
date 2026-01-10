import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { gameApi, teamApi } from '../services/api'
import { GameCard } from '../components/Game'
import { useApiData, useToggle, useFormState, useGames } from '../hooks'
import { Loader } from '../components/Loader'
import Tabs from '../components/Tabs'

function GamesPage() {
  const navigate = useNavigate()
  const { value: showForm, toggle: toggleForm } = useToggle(false)
  const { formData: newGame, updateField, resetForm } = useFormState({ homeId: '', awayId: '' })
  const [activeTab, setActiveTab] = useState('all')

  const loadGamesData = async () => {
    const [gamesData, teamsData] = await Promise.all([
      gameApi.getAll(),
      teamApi.getAll(),
    ])

    const playersMap = {}
    for (const game of gamesData ?? []) {
      if (game?.id) {
        const players = await gameApi.getPlayersForGame(game.id)
        playersMap[game.id] = players ?? { home: [], away: [] }
      }
    }

    return {
      games: gamesData ?? [],
      teams: teamsData ?? [],
      gamePlayers: playersMap,
    }
  }

  const { data, loading, reload } = useApiData(loadGamesData)
  const allGames = data?.games ?? []
  const teams = data?.teams ?? []
  const gamePlayers = data?.gamePlayers ?? {}

  // Filter games by tab
  const filteredGames = activeTab === 'all'
    ? allGames
    : allGames.filter(game => game.state === activeTab.toUpperCase())

  // Count games by state
  const gameCounts = {
    all: allGames.length,
    ready: allGames.filter(g => g.state === 'READY').length,
    running: allGames.filter(g => g.state === 'RUNNING').length,
    paused: allGames.filter(g => g.state === 'PAUSED').length,
    ended: allGames.filter(g => g.state === 'ENDED').length,
  }

  // Define tabs
  const tabs = [
    { id: 'all', label: 'All', count: gameCounts.all },
    { id: 'running', label: 'Running', count: gameCounts.running },
    { id: 'paused', label: 'Paused', count: gameCounts.paused },
    { id: 'ready', label: 'Ready', count: gameCounts.ready },
    { id: 'ended', label: 'Ended', count: gameCounts.ended },
  ]

  const {
    createGame,
    startGame,
    pauseGame,
    resumeGame,
    endGame,
    recordScore,
    deleteGame,
  } = useGames({ reload })

  const handleCreateGame = async (e) => {
    e.preventDefault()
    const success = await createGame(newGame.homeId, newGame.awayId)
    if (success) {
      resetForm()
      toggleForm()
    }
  }

  if (loading) {
    return <Loader text="Loading games..." />
  }

  return (
    <div>
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Games</h1>
          <p className="page-subtitle">Manage games and track scores</p>
        </div>
        <button className="btn btn-primary" onClick={toggleForm}>
          <Plus size={18} />
          New Game
        </button>
      </div>

      {showForm && (
        <div className="card mb-4">
          <h3 className="card-title mb-4">Create New Game</h3>
          <form onSubmit={handleCreateGame}>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Home Team</label>
                <select
                  className="form-select"
                  value={newGame.homeId}
                  onChange={(e) => updateField('homeId', e.target.value)}
                >
                  <option value="">Select team...</option>
                  {teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Away Team</label>
                <select
                  className="form-select"
                  value={newGame.awayId}
                  onChange={(e) => updateField('awayId', e.target.value)}
                >
                  <option value="">Select team...</option>
                  {teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group" style={{ alignSelf: 'flex-end' }}>
                <button type="submit" className="btn btn-success">
                  Create
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Games Grid */}
      {filteredGames.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>No {activeTab !== 'all' ? activeTab : ''} games yet</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-2">
          {filteredGames.map((game, index) => (
            <GameCard
              key={game?.id ?? `game-${index}`}
              game={game}
              players={gamePlayers[game?.id] ?? { home: [], away: [] }}
              showControls={true}
              showDeleteButton={true}
              showWatchButton={true}
              onStart={startGame}
              onPause={pauseGame}
              onResume={resumeGame}
              onEnd={endGame}
              onScore={recordScore}
              onDelete={deleteGame}
              onClick={(gameId) => navigate(`/games/${gameId}`)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default GamesPage
