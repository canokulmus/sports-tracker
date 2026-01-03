import { Plus } from 'lucide-react'
import { gameApi, teamApi } from '../services/api'
import { GameCard } from '../components/Game'
import { useMockData, useToggle, useFormState } from '../hooks'
import { Loader } from '../components/Loader'

function GamesPage() {
  const { value: showForm, toggle: toggleForm } = useToggle(false)
  const { formData: newGame, updateField, resetForm } = useFormState({ homeId: '', awayId: '' })

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

  const { data, loading, reload } = useMockData(loadGamesData)
  const games = data?.games ?? []
  const teams = data?.teams ?? []
  const gamePlayers = data?.gamePlayers ?? {}

  const handleCreateGame = async (e) => {
    e.preventDefault()
    if (!newGame.homeId || !newGame.awayId) return
    if (newGame.homeId === newGame.awayId) {
      alert('You cannot select the same team!')
      return
    }

    try {
      await gameApi.create(parseInt(newGame.homeId), parseInt(newGame.awayId))
      resetForm()
      toggleForm()
      reload()
    } catch (error) {
      console.error('Error creating game:', error)
      alert('Could not create game')
    }
  }

  const handleGameAction = async (actionFn, id) => {
    try {
      await actionFn(id)
      reload()
    } catch (error) {
      console.error('Action error:', error)
    }
  }

  const handleStart = (id) => handleGameAction(gameApi.start, id)
  const handlePause = (id) => handleGameAction(gameApi.pause, id)
  const handleResume = (id) => handleGameAction(gameApi.resume, id)
  const handleEnd = (id) => handleGameAction(gameApi.end, id)

  const handleScore = async (gameId, side, playerName) => {
    try {
      await gameApi.score(gameId, side, playerName, 1)
      reload()
    } catch (error) {
      console.error('Error recording goal:', error)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this game?')) return
    try {
      await gameApi.delete(id)
      reload()
    } catch (error) {
      console.error('Error deleting game:', error)
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

      {games.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>No games yet</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-2">
          {games.map((game) => (
            <GameCard
              key={game?.id ?? Math.random()}
              game={game}
              players={gamePlayers[game?.id] ?? { home: [], away: [] }}
              showControls={true}
              showDeleteButton={true}
              onStart={handleStart}
              onPause={handlePause}
              onResume={handleResume}
              onEnd={handleEnd}
              onScore={handleScore}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default GamesPage
