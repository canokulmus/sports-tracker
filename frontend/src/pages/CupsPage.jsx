// src/pages/CupsPage.jsx
import { useState, useEffect } from 'react'
import { Plus, Trophy, ChevronRight } from 'lucide-react'
import { cupApi, teamApi } from '../services/api'

function CupsPage() {
  const [cups, setCups] = useState([])
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedCup, setSelectedCup] = useState(null)
  const [standings, setStandings] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [newCup, setNewCup] = useState({ name: '', type: 'LEAGUE', teamIds: [] })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    const [cupsData, teamsData] = await Promise.all([
      cupApi.getAll(),
      teamApi.getAll(),
    ])
    setCups(cupsData)
    setTeams(teamsData)
    setLoading(false)
  }

  // Turnuva seç ve standings yükle
  const handleSelectCup = async (cup) => {
    setSelectedCup(cup)
    const standingsData = await cupApi.getStandings(cup.id)
    setStandings(standingsData)
  }

  // Turnuva oluştur
  const handleCreateCup = async (e) => {
    e.preventDefault()
    if (!newCup.name || newCup.teamIds.length < 2) {
      alert('En az 2 takım seçmelisiniz!')
      return
    }

    await cupApi.create(newCup.name, newCup.type, newCup.teamIds)
    setNewCup({ name: '', type: 'LEAGUE', teamIds: [] })
    setShowForm(false)
    loadData()
  }

  // Takım seçimi toggle
  const toggleTeamSelection = (teamId) => {
    setNewCup((prev) => ({
      ...prev,
      teamIds: prev.teamIds.includes(teamId)
        ? prev.teamIds.filter((id) => id !== teamId)
        : [...prev.teamIds, teamId],
    }))
  }

  // Turnuva türü badge
  const TypeBadge = ({ type }) => {
    const colors = {
      LEAGUE: '#3b82f6',
      ELIMINATION: '#ef4444',
      GROUP: '#22c55e',
    }
    return (
      <span
        className="badge"
        style={{ backgroundColor: colors[type] || '#666', color: 'white' }}
      >
        {type}
      </span>
    )
  }

  if (loading) {
    return <div className="text-center text-muted">Yükleniyor...</div>
  }

  return (
    <div>
      {/* Header */}
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Turnuvalar</h1>
          <p className="page-subtitle">Lig, kupa ve grup turnuvalarını yönet</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          <Plus size={18} />
          Yeni Turnuva
        </button>
      </div>

      {/* Yeni Turnuva Formu */}
      {showForm && (
        <div className="card mb-4">
          <h3 className="card-title mb-4">Yeni Turnuva Oluştur</h3>
          <form onSubmit={handleCreateCup}>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Turnuva Adı</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="örn: Süper Lig 2024-25"
                  value={newCup.name}
                  onChange={(e) => setNewCup({ ...newCup, name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Turnuva Türü</label>
                <select
                  className="form-select"
                  value={newCup.type}
                  onChange={(e) => setNewCup({ ...newCup, type: e.target.value })}
                >
                  <option value="LEAGUE">Lig (Round Robin)</option>
                  <option value="ELIMINATION">Eleme (Knockout)</option>
                  <option value="GROUP">Grup + Playoff</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">
                Takımlar ({newCup.teamIds.length} seçili)
              </label>
              <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
                {teams.map((team) => (
                  <button
                    key={team.id}
                    type="button"
                    className={`btn btn-sm ${
                      newCup.teamIds.includes(team.id)
                        ? 'btn-primary'
                        : 'btn-secondary'
                    }`}
                    onClick={() => toggleTeamSelection(team.id)}
                  >
                    {team.name}
                  </button>
                ))}
              </div>
            </div>

            <button type="submit" className="btn btn-success">
              Turnuva Oluştur
            </button>
          </form>
        </div>
      )}

      <div className="grid grid-2">
        {/* Sol: Turnuva Listesi */}
        <div>
          <div className="card">
            <h3 className="card-title mb-4">Turnuvalar ({cups.length})</h3>

            {cups.length === 0 ? (
              <div className="empty-state">
                <Trophy size={48} />
                <p>Henüz turnuva yok</p>
              </div>
            ) : (
              <div>
                {cups.map((cup) => (
                  <div
                    key={cup.id}
                    className="card"
                    style={{
                      cursor: 'pointer',
                      borderColor:
                        selectedCup?.id === cup.id ? '#3b82f6' : undefined,
                    }}
                    onClick={() => handleSelectCup(cup)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="flex items-center gap-2 mb-4">
                          <Trophy size={20} />
                          <strong>{cup.name}</strong>
                        </div>
                        <div className="flex gap-2 items-center">
                          <TypeBadge type={cup.type} />
                          <span className="text-muted text-sm">
                            {cup.teams.length} takım • {cup.gameCount} maç
                          </span>
                        </div>
                      </div>
                      <ChevronRight size={20} className="text-muted" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sağ: Puan Durumu */}
        <div>
          {selectedCup ? (
            <div className="card">
              <h3 className="card-title mb-4">{selectedCup.name} - Puan Durumu</h3>

              <table className="table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Takım</th>
                    <th>O</th>
                    <th>G</th>
                    <th>B</th>
                    <th>M</th>
                    <th>AG</th>
                    <th>YG</th>
                    <th>AV</th>
                    <th>P</th>
                  </tr>
                </thead>
                <tbody>
                  {standings.map((row, index) => (
                    <tr key={row.team}>
                      <td>
                        <strong>{index + 1}</strong>
                      </td>
                      <td>
                        <strong>{row.team}</strong>
                      </td>
                      <td>{row.played}</td>
                      <td className="text-success">{row.won}</td>
                      <td>{row.draw}</td>
                      <td className="text-danger">{row.lost}</td>
                      <td>{row.gf}</td>
                      <td>{row.ga}</td>
                      <td>{row.gf - row.ga}</td>
                      <td>
                        <strong>{row.points}</strong>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="card">
              <div className="empty-state">
                <Trophy size={48} />
                <p>Puan durumunu görmek için bir turnuva seçin</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CupsPage