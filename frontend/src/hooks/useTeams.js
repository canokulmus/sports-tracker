import { teamApi } from '../services/api'
import { useDialog } from '../context/DialogContext'

export function useTeams({ reload, selectedTeam, selectTeam }) {
  const { confirm } = useDialog()

  const createTeam = async (teamName) => {
    if (!teamName.trim()) return false

    await teamApi.create(teamName)
    reload()
    return true
  }

  const deleteTeam = async (id) => {
    confirm({
      title: 'Delete Team',
      message: 'Are you sure you want to delete this team? This action cannot be undone.',
      confirmText: 'Delete',
      cancelText: 'Cancel',
      onConfirm: async () => {
        await teamApi.delete(id)
        reload()
      },
    })
  }

  const addPlayer = async (playerName, jerseyNo) => {
    if (!playerName || !jerseyNo || !selectedTeam) return false

    await teamApi.addPlayer(selectedTeam.id, playerName, parseInt(jerseyNo))
    reload()

    const updated = await teamApi.getById(selectedTeam.id)
    selectTeam(updated)
    return true
  }

  const removePlayer = async (playerName) => {
    confirm({
      title: 'Remove Player',
      message: `Are you sure you want to remove ${playerName} from the team?`,
      confirmText: 'Remove',
      cancelText: 'Cancel',
      onConfirm: async () => {
        if (!selectedTeam) return
        await teamApi.removePlayer(selectedTeam.id, playerName)
        reload()

        const updated = await teamApi.getById(selectedTeam.id)
        selectTeam(updated)
      },
    })
  }

  const addCustomField = async (key, value) => {
    if (!selectedTeam) return false

    await teamApi.setCustomField(selectedTeam.id, key, value)
    reload()

    const updated = await teamApi.getById(selectedTeam.id)
    selectTeam(updated)
    return true
  }

  const deleteCustomField = async (key) => {
    if (!selectedTeam) return false

    await teamApi.deleteCustomField(selectedTeam.id, key)
    reload()

    const updated = await teamApi.getById(selectedTeam.id)
    selectTeam(updated)
    return true
  }

  return {
    createTeam,
    deleteTeam,
    addPlayer,
    removePlayer,
    addCustomField,
    deleteCustomField,
  }
}
