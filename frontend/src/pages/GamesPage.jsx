import { Plus } from 'lucide-react'
import { gameApi, teamApi } from '../services/api'
import { GameCard } from '../components/Game'
import { useMockData, useToggle, useFormState, useGames } from '../hooks'
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

      {games.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>No games yet</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-2">
          {games.map((game, index) => (
            <GameCard
              key={game?.id ?? `game-${index}`}
              game={game}
              players={gamePlayers[game?.id] ?? { home: [], away: [] }}
              showControls={true}
              showDeleteButton={true}
              onStart={startGame}
              onPause={pauseGame}
              onResume={resumeGame}
              onEnd={endGame}
              onScore={recordScore}
              onDelete={deleteGame}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default GamesPage
