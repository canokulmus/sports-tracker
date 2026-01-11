import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, Filter, X } from 'lucide-react'
import { gameApi, teamApi, cupApi } from '../services/api'
import { GameCard } from '../components/Game'
import { useApiData, useToggle, useFormState, useGames } from '../hooks'
import { Loader } from '../components/Loader'
import Tabs from '../components/Tabs'

function GamesPage() {
  const navigate = useNavigate()
  const { value: showForm, toggle: toggleForm } = useToggle(false)
  const { value: showSearchFilters, toggle: toggleSearchFilters } = useToggle(false)
  const { formData: newGame, updateField, resetForm } = useFormState({ homeId: '', awayId: '' })
  const [activeTab, setActiveTab] = useState('all')

  const [searchParams, setSearchParams] = useState({
    teamName: '',
    group: '',
    startDate: '',
    endDate: '',
    cupId: ''
  })
  const [isSearchActive, setIsSearchActive] = useState(false)
  const [searchResults, setSearchResults] = useState([])
  const [cups, setCups] = useState([])

  const loadGamesData = async () => {
    const [gamesData, teamsData, cupsData] = await Promise.all([
      gameApi.getAll(),
      teamApi.getAll(),
      cupApi.getAll(),
    ])

    setCups(cupsData ?? [])

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

  const handleSearch = async (e) => {
    e.preventDefault()

    const hasSearchParams = Object.values(searchParams).some(val => val !== '')

    if (!hasSearchParams) {
      setIsSearchActive(false)
      setSearchResults([])
      return
    }

    try {
      const searchQuery = { ...searchParams }
      if (searchQuery.startDate) {
        searchQuery.startDate = new Date(searchQuery.startDate).toISOString()
      }
      if (searchQuery.endDate) {
        const endDate = new Date(searchQuery.endDate)
        endDate.setHours(23, 59, 59, 999)
        searchQuery.endDate = endDate.toISOString()
      }

      const results = await gameApi.search(searchQuery)
      setSearchResults(results)
      setIsSearchActive(true)

      const playersMap = {}
      for (const game of results) {
        if (game?.id) {
          const players = await gameApi.getPlayersForGame(game.id)
          playersMap[game.id] = players ?? { home: [], away: [] }
        }
      }

      data.gamePlayers = { ...data.gamePlayers, ...playersMap }
    } catch (error) {
      console.error('Search failed:', error)
    }
  }

  const updateSearchParam = (key, value) => {
    setSearchParams(prev => ({ ...prev, [key]: value }))
  }

  const clearSearch = () => {
    setSearchParams({
      teamName: '',
      group: '',
      startDate: '',
      endDate: '',
      cupId: ''
    })
    setIsSearchActive(false)
    setSearchResults([])
  }

  const { data, loading, reload } = useApiData(loadGamesData)
  const allGames = data?.games ?? []
  const teams = data?.teams ?? []
  const gamePlayers = data?.gamePlayers ?? {}

  const displayGames = isSearchActive ? searchResults : allGames

  const filteredGames = activeTab === 'all'
    ? displayGames
    : displayGames.filter(game => game.state === activeTab.toUpperCase())

  const gameCounts = {
    all: displayGames.length,
    ready: displayGames.filter(g => g.state === 'READY').length,
    running: displayGames.filter(g => g.state === 'RUNNING').length,
    paused: displayGames.filter(g => g.state === 'PAUSED').length,
    ended: displayGames.filter(g => g.state === 'ENDED').length,
  }

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

      <div className="card mb-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="card-title">Search Games</h3>
          {isSearchActive && (
            <button onClick={clearSearch} className="btn btn-secondary btn-sm">
              <X size={16} />
              Clear Search
            </button>
          )}
          <button onClick={toggleSearchFilters} className="btn btn-secondary btn-sm">
            <Filter size={16} />
            {showSearchFilters ? 'Hide Filters' : 'Show Filters'}
          </button>
        </div>

        <form onSubmit={handleSearch}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Team Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="Search by team name..."
                value={searchParams.teamName}
                onChange={(e) => updateSearchParam('teamName', e.target.value)}
              />
            </div>

            <div className="form-group" style={{ alignSelf: 'flex-end' }}>
              <button type="submit" className="btn btn-primary">
                <Search size={16} />
                Search
              </button>
            </div>
          </div>

          {showSearchFilters && (
            <div className="form-row mt-3">
              <div className="form-group">
                <label className="form-label">Group</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., A, B, C..."
                  value={searchParams.group}
                  onChange={(e) => updateSearchParam('group', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Tournament</label>
                <select
                  className="form-select"
                  value={searchParams.cupId}
                  onChange={(e) => updateSearchParam('cupId', e.target.value)}
                >
                  <option value="">All Tournaments</option>
                  {cups.map((cup) => (
                    <option key={cup.id} value={cup.id}>
                      {cup.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Start Date</label>
                <input
                  type="date"
                  className="form-input"
                  value={searchParams.startDate}
                  onChange={(e) => updateSearchParam('startDate', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">End Date</label>
                <input
                  type="date"
                  className="form-input"
                  value={searchParams.endDate}
                  onChange={(e) => updateSearchParam('endDate', e.target.value)}
                />
              </div>
            </div>
          )}
        </form>

        {isSearchActive && (
          <div className="mt-3 text-sm" style={{ color: '#6b7280' }}>
            Found {searchResults.length} game{searchResults.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

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
