import { useState } from 'react'
import { Plus, Trash2, UserPlus, X, Users } from 'lucide-react'
import { teamApi } from '../services/api'
import { useMockData, useSelection, useFormState } from '../hooks'
import { Loader } from '../components/Loader'

function TeamsPage() {
  const [newTeamName, setNewTeamName] = useState('')
  const { selected: selectedTeam, select: selectTeam, clear: clearSelection } = useSelection()
  const { formData: newPlayer, updateField, resetForm } = useFormState({ name: '', no: '' })

  const { data: teams, loading, reload } = useMockData(() => teamApi.getAll())

  const handleCreateTeam = async (e) => {
    e.preventDefault()
    if (!newTeamName.trim()) return

    await teamApi.create(newTeamName)
    setNewTeamName('')
    reload()
  }

  const handleDeleteTeam = async (id) => {
    if (!confirm('Takımı silmek istediğinize emin misiniz?')) return
    await teamApi.delete(id)
    reload()
  }

  const handleAddPlayer = async (e) => {
    e.preventDefault()
    if (!newPlayer.name || !newPlayer.no || !selectedTeam) return

    await teamApi.addPlayer(selectedTeam.id, newPlayer.name, parseInt(newPlayer.no))
    resetForm()
    reload()

    const updated = await teamApi.getById(selectedTeam.id)
    selectTeam(updated)
  }

  const handleRemovePlayer = async (playerName) => {
    if (!selectedTeam) return
    await teamApi.removePlayer(selectedTeam.id, playerName)
    reload()

    const updated = await teamApi.getById(selectedTeam.id)
    selectTeam(updated)
  }

  if (loading) {
    return <Loader text="Takımlar yükleniyor..." />
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Takımlar</h1>
        <p className="page-subtitle">Takımları yönet ve oyuncu ekle</p>
      </div>

      <div className="grid grid-2">
        <div>
          <div className="card">
            <form onSubmit={handleCreateTeam} className="flex gap-2">
              <input
                type="text"
                className="form-input"
                placeholder="Yeni takım adı..."
                value={newTeamName}
                onChange={(e) => setNewTeamName(e.target.value)}
              />
              <button type="submit" className="btn btn-primary">
                <Plus size={18} />
                Ekle
              </button>
            </form>
          </div>

          <div className="card">
            <h3 className="card-title mb-4">Tüm Takımlar ({teams?.length ?? 0})</h3>

            {!teams || teams.length === 0 ? (
              <div className="empty-state">
                <p>Henüz takım yok</p>
              </div>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Takım Adı</th>
                    <th>Oyuncu</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {teams.map((team) => (
                    <tr
                      key={team.id}
                      onClick={() => selectTeam(team)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td>{team.id}</td>
                      <td>
                        <strong>{team.name}</strong>
                      </td>
                      <td>{Object.keys(team.players).length}</td>
                      <td className="text-right">
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteTeam(team.id)
                          }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div>
          {selectedTeam ? (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">{selectedTeam.name}</h3>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={clearSelection}
                >
                  <X size={14} />
                </button>
              </div>

              <form onSubmit={handleAddPlayer} className="mb-4">
                <div className="form-row">
                  <div className="form-group">
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Oyuncu adı"
                      value={newPlayer.name}
                      onChange={(e) => updateField('name', e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <input
                      type="number"
                      className="form-input"
                      placeholder="Forma No"
                      value={newPlayer.no}
                      onChange={(e) => updateField('no', e.target.value)}
                    />
                  </div>
                  <button type="submit" className="btn btn-success">
                    <UserPlus size={18} />
                    <span className="ml-2">Oyuncu Ekle</span>
                  </button>
                </div>
              </form>

              <h4 className="text-muted mb-4">Kadro</h4>
              {Object.keys(selectedTeam.players).length === 0 ? (
                <p className="text-muted">Henüz oyuncu yok</p>
              ) : (
                <table className="table">
                  <thead>
                    <tr>
                      <th>No</th>
                      <th>İsim</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(selectedTeam.players).map(([name, data]) => (
                      <tr key={name}>
                        <td>
                          <span className="badge badge-primary">{data.no}</span>
                        </td>
                        <td>{name}</td>
                        <td className="text-right">
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => handleRemovePlayer(name)}
                          >
                            <Trash2 size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          ) : (
            <div className="card">
              <div className="empty-state">
                <Users size={48} className="empty-state-icon" />
                <p>Detayları görmek için bir takım seçin</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TeamsPage
