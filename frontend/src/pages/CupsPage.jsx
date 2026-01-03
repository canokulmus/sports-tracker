import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trophy, ChevronRight } from 'lucide-react'
import { cupApi, teamApi } from '../services/api'
import { colors } from '../styles/colors'
import { useMockData, useToggle, useMultiSelection } from '../hooks'
import { Loader } from '../components/Loader'

function TypeBadge({ type }) {
  const tournamentColors = {
    LEAGUE: colors.tournament.league,
    ELIMINATION: colors.tournament.elimination,
    GROUP: colors.tournament.group,
  }
  return (
    <span
      className="badge"
      style={{
        backgroundColor: tournamentColors[type] || colors.text.muted,
        color: colors.quickColors.white,
      }}
    >
      {type}
    </span>
  )
}

function CupsPage() {
  const navigate = useNavigate()
  const [newCupName, setNewCupName] = useState('')
  const [cupType, setCupType] = useState('LEAGUE')

  const { value: showForm, toggle: toggleForm } = useToggle(false)
  const { selected: selectedTeamIds, toggleItem: toggleTeam, isSelected } = useMultiSelection([])

  const loadCupsData = async () => {
    const [cupsData, teamsData] = await Promise.all([
      cupApi.getAll(),
      teamApi.getAll(),
    ])
    return { cups: cupsData, teams: teamsData }
  }

  const { data, loading, reload } = useMockData(loadCupsData)
  const cups = data?.cups ?? []
  const teams = data?.teams ?? []

  const handleSelectCup = (cup) => {
    navigate(`/cups/${cup.id}`)
  }

  const handleCreateCup = async (e) => {
    e.preventDefault()
    if (!newCupName || selectedTeamIds.length < 2) {
      alert('En az 2 takım seçmelisiniz!')
      return
    }

    await cupApi.create(newCupName, cupType, selectedTeamIds)
    setNewCupName('')
    setCupType('LEAGUE')
    toggleForm()
    reload()
  }

  if (loading) {
    return <Loader text="Turnuvalar yükleniyor..." />
  }

  return (
    <div>
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Turnuvalar</h1>
          <p className="page-subtitle">Lig, kupa ve grup turnuvalarını yönet</p>
        </div>
        <button className="btn btn-primary" onClick={toggleForm}>
          <Plus size={18} />
          Yeni Turnuva
        </button>
      </div>

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
                  value={newCupName}
                  onChange={(e) => setNewCupName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Turnuva Türü</label>
                <select
                  className="form-select"
                  value={cupType}
                  onChange={(e) => setCupType(e.target.value)}
                >
                  <option value="LEAGUE">Lig (Round Robin)</option>
                  <option value="ELIMINATION">Eleme (Knockout)</option>
                  <option value="GROUP">Grup + Playoff</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">
                Takımlar ({selectedTeamIds.length} seçili)
              </label>
              <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
                {teams.map((team) => (
                  <button
                    key={team.id}
                    type="button"
                    className={`btn btn-sm ${
                      isSelected(team.id) ? 'btn-primary' : 'btn-secondary'
                    }`}
                    onClick={() => toggleTeam(team.id)}
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

      <div className="card">
        <h3 className="card-title mb-4">Turnuvalar ({cups.length})</h3>

        {cups.length === 0 ? (
          <div className="empty-state">
            <Trophy size={48} />
            <p>Henüz turnuva yok</p>
          </div>
        ) : (
          <div className="grid grid-3">
            {cups.map((cup) => (
              <div
                key={cup.id}
                className="card game-card-hover"
                style={{
                  cursor: 'pointer',
                }}
                onClick={() => handleSelectCup(cup)}
              >
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center gap-2">
                    <Trophy size={20} color={colors.brand.primary} />
                    <strong>{cup.name}</strong>
                  </div>
                  <ChevronRight size={20} className="text-muted" />
                </div>
                <div className="flex gap-2 items-center">
                  <TypeBadge type={cup.type} />
                  <span className="text-muted" style={{ fontSize: '13px' }}>
                    {cup.teams.length} takım • {cup.gameCount} maç
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default CupsPage
