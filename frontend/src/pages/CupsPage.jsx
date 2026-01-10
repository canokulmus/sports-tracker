import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trophy, ChevronRight, Trash2 } from 'lucide-react'
import { cupApi, teamApi } from '../services/api'
import { colors } from '../styles/colors'
import { useApiData, useToggle, useMultiSelection } from '../hooks'
import { Loader } from '../components/Loader'
import { useDialog } from '../context/DialogContext'

function TypeBadge({ type }) {
  const tournamentColors = {
    LEAGUE: colors.tournament.league,
    LEAGUE2: colors.tournament.league,
    ELIMINATION: colors.tournament.elimination,
    ELIMINATION2: colors.tournament.elimination,
    GROUP: colors.tournament.group,
    GROUP2: colors.tournament.group,
  }

  const displayNames = {
    LEAGUE: 'LEAGUE',
    LEAGUE2: 'LEAGUE2',
    ELIMINATION: 'ELIMINATION',
    ELIMINATION2: 'ELIMINATION2',
    GROUP: 'GROUP',
    GROUP2: 'GROUP2',
  }

  return (
    <span
      className="badge"
      style={{
        backgroundColor: tournamentColors[type] || colors.text.muted,
        color: colors.quickColors.white,
      }}
    >
      {displayNames[type] || type}
    </span>
  )
}

function CupsPage() {
  const navigate = useNavigate()
  const [newCupName, setNewCupName] = useState('')
  const [cupType, setCupType] = useState('LEAGUE')
  const [numGroups, setNumGroups] = useState(4)
  const [playoffTeams, setPlayoffTeams] = useState(8)
  const { alert, confirm } = useDialog()

  const { value: showForm, toggle: toggleForm } = useToggle(false)
  const { selected: selectedTeamIds, toggleItem: toggleTeam, isSelected } = useMultiSelection([])

  const loadCupsData = async () => {
    const [cupsData, teamsData] = await Promise.all([
      cupApi.getAll(),
      teamApi.getAll(),
    ])
    return { cups: cupsData, teams: teamsData }
  }

  const { data, loading, reload } = useApiData(loadCupsData)
  const cups = data?.cups ?? []
  const teams = data?.teams ?? []

  const handleSelectCup = (cup) => {
    navigate(`/cups/${cup.id}`)
  }

  const handleCreateCup = async (e) => {
    e.preventDefault()
    if (!newCupName || selectedTeamIds.length < 2) {
      alert({
        title: 'Invalid Tournament',
        message: 'You must select at least 2 teams to create a tournament!',
      })
      return
    }

    // Validation for GROUP tournaments
    if (cupType === 'GROUP' || cupType === 'GROUP2') {
      if (selectedTeamIds.length < numGroups * 2) {
        alert({
          title: 'Invalid Configuration',
          message: `You need at least ${numGroups * 2} teams for ${numGroups} groups (minimum 2 teams per group)!`,
        })
        return
      }
      if (playoffTeams > selectedTeamIds.length) {
        alert({
          title: 'Invalid Configuration',
          message: `Playoff teams (${playoffTeams}) cannot exceed total teams (${selectedTeamIds.length})!`,
        })
        return
      }
    }

    await cupApi.create(newCupName, cupType, selectedTeamIds, numGroups, playoffTeams)
    setNewCupName('')
    setCupType('LEAGUE')
    setNumGroups(4)
    setPlayoffTeams(8)
    toggleForm()
    reload()
  }

  const handleDeleteCup = (e, cup) => {
    e.stopPropagation() // Prevent navigation when clicking delete
    confirm({
      title: 'Delete Tournament',
      message: `Are you sure you want to delete "${cup.name}"? This will also delete all ${cup.gameCount} games in this tournament.`,
      confirmText: 'Delete',
      cancelText: 'Cancel',
      onConfirm: async () => {
        try {
          await cupApi.delete(cup.id)
          reload()
        } catch (error) {
          console.error('Failed to delete tournament:', error)
        }
      },
    })
  }

  if (loading) {
    return <Loader text="Loading tournaments..." />
  }

  return (
    <div>
      <div className="page-header flex justify-between items-center">
        <div>
          <h1 className="page-title">Tournaments</h1>
          <p className="page-subtitle">Manage league, cup and group tournaments</p>
        </div>
        <button className="btn btn-primary" onClick={toggleForm}>
          <Plus size={18} />
          New Tournament
        </button>
      </div>

      {showForm && (
        <div className="card mb-4">
          <h3 className="card-title mb-4">Create New Tournament</h3>
          <form onSubmit={handleCreateCup}>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Tournament Name</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Premier League 2024-25"
                  value={newCupName}
                  onChange={(e) => setNewCupName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Tournament Type</label>
                <select
                  className="form-select"
                  value={cupType}
                  onChange={(e) => setCupType(e.target.value)}
                >
                  <option value="LEAGUE">League (Round Robin)</option>
                  <option value="LEAGUE2">League 2 (Home & Away)</option>
                  <option value="ELIMINATION">Elimination (Knockout)</option>
                  <option value="ELIMINATION2">Elimination 2 (Two-Leg)</option>
                  <option value="GROUP">Group + Playoff</option>
                  <option value="GROUP2">Group 2 + Playoff (Home & Away)</option>
                </select>
              </div>
            </div>

            {(cupType === 'GROUP' || cupType === 'GROUP2') && (
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Number of Groups</label>
                  <input
                    type="number"
                    className="form-input"
                    min="2"
                    max="8"
                    value={numGroups}
                    onChange={(e) => setNumGroups(parseInt(e.target.value) || 2)}
                  />
                  <small className="form-help">
                    Teams will be divided into {numGroups} groups
                  </small>
                </div>
                <div className="form-group">
                  <label className="form-label">Playoff Teams</label>
                  <input
                    type="number"
                    className="form-input"
                    min="2"
                    max="32"
                    value={playoffTeams}
                    onChange={(e) => setPlayoffTeams(parseInt(e.target.value) || 2)}
                  />
                  <small className="form-help">
                    Top teams advancing to playoffs
                  </small>
                </div>
              </div>
            )}

            <div className="form-group">
              <label className="form-label">
                Teams ({selectedTeamIds.length} selected)
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
              Create Tournament
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h3 className="card-title mb-4">Tournaments ({cups.length})</h3>

        {cups.length === 0 ? (
          <div className="empty-state">
            <Trophy size={48} />
            <p>No tournaments yet</p>
          </div>
        ) : (
          <div className="grid grid-3">
            {cups.map((cup) => (
              <div
                key={cup.id}
                className="card game-card-hover"
                style={{
                  cursor: 'pointer',
                  position: 'relative',
                }}
                onClick={() => handleSelectCup(cup)}
              >
                <button
                  onClick={(e) => handleDeleteCup(e, cup)}
                  style={{
                    position: 'absolute',
                    top: '12px',
                    right: '12px',
                    padding: '6px',
                    borderRadius: '6px',
                    border: 'none',
                    background: 'transparent',
                    color: colors.text.muted,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = `${colors.state.danger}15`
                    e.currentTarget.style.color = colors.state.danger
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent'
                    e.currentTarget.style.color = colors.text.muted
                  }}
                >
                  <Trash2 size={16} />
                </button>
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
                    {cup.teams.length} teams • {cup.gameCount} games
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
