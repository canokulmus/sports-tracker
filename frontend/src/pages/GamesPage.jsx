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
      alert('Aynı takımı seçemezsiniz!')
      return
    }

    try {
      await gameApi.create(parseInt(newGame.homeId), parseInt(newGame.awayId))
      resetForm()
      toggleForm()
      reload()
    } catch (error) {
      console.error('Maç oluşturulurken hata:', error)
      alert('Maç oluşturulamadı')
    }
  }

  const handleGameAction = async (actionFn, id) => {
    try {
      await actionFn(id)
      reload()
    } catch (error) {
      console.error('İşlem hatası:', error)
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
      console.error('Gol kaydedilirken hata:', error)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Maçı silmek istediğinize emin misiniz?')) return
    try {
      await gameApi.delete(id)
      reload()
    } catch (error) {
      console.error('Maç silinirken hata:', error)
    }
  }

  if (loading) {
    return <Loader text="Maçlar yükleniyor..." />
  }

  return (
    <div>
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Maçlar</h1>
          <p className="page-subtitle">Maçları yönet ve skorları takip et</p>
        </div>
        <button className="btn btn-primary" onClick={toggleForm}>
          <Plus size={18} />
          Yeni Maç
        </button>
      </div>

      {showForm && (
        <div className="card mb-4">
          <h3 className="card-title mb-4">Yeni Maç Oluştur</h3>
          <form onSubmit={handleCreateGame}>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Ev Sahibi</label>
                <select
                  className="form-select"
                  value={newGame.homeId}
                  onChange={(e) => updateField('homeId', e.target.value)}
                >
                  <option value="">Takım seçin...</option>
                  {teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Deplasman</label>
                <select
                  className="form-select"
                  value={newGame.awayId}
                  onChange={(e) => updateField('awayId', e.target.value)}
                >
                  <option value="">Takım seçin...</option>
                  {teams.map((team) => (
                    <option key={team.id} value={team.id}>
                      {team.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group" style={{ alignSelf: 'flex-end' }}>
                <button type="submit" className="btn btn-success">
                  Oluştur
                </button>
              </div>
            </div>
          </form>
        </div>
      )}

      {games.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>Henüz maç yok</p>
          </div>
        </div>
      ) : (
        <div>
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

      <style>{`
        .goal-dropdown {
          position: relative;
          display: inline-block;
        }

        .dropdown-menu {
          position: absolute;
          top: 100%;
          left: 50%;
          transform: translateX(-50%);
          background: var(--bg-secondary);
          border: 1px solid var(--border);
          border-radius: 8px;
          min-width: 180px;
          z-index: 1000;
          margin-top: 4px;
          box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }

        .dropdown-header {
          padding: 8px 12px;
          font-size: 0.75rem;
          color: var(--text-secondary);
          border-bottom: 1px solid var(--border);
        }

        .dropdown-item {
          padding: 10px 12px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .dropdown-item:hover {
          background: var(--bg-card);
        }

        .dropdown-item.disabled {
          color: var(--text-secondary);
          cursor: not-allowed;
        }

        .dropdown-divider {
          height: 1px;
          background: var(--border);
          margin: 4px 0;
        }

        .scorers-list {
          margin-top: 8px;
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .scorer-item {
          font-size: 0.75rem;
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  )
}

export default GamesPage
