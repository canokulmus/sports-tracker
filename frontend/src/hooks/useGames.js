import { gameApi } from '../services/api'
import { useDialog } from '../context/DialogContext'

export function useGames({ reload }) {
  const { confirm, alert } = useDialog()

  const createGame = async (homeId, awayId) => {
    if (!homeId || !awayId) return false

    if (homeId === awayId) {
      alert({
        title: 'Invalid Selection',
        message: 'You cannot select the same team for both home and away!',
      })
      return false
    }

    try {
      await gameApi.create(parseInt(homeId), parseInt(awayId))
      reload()
      return true
    } catch (error) {
      console.error('Error creating game:', error)
      alert({
        title: 'Error',
        message: 'Could not create game. Please try again.',
      })
      return false
    }
  }

  const startGame = async (id) => {
    try {
      await gameApi.start(id)
      reload()
    } catch (error) {
      console.error('Error starting game:', error)
    }
  }

  const pauseGame = async (id) => {
    try {
      await gameApi.pause(id)
      reload()
    } catch (error) {
      console.error('Error pausing game:', error)
    }
  }

  const resumeGame = async (id) => {
    try {
      await gameApi.resume(id)
      reload()
    } catch (error) {
      console.error('Error resuming game:', error)
    }
  }

  const endGame = async (id) => {
    try {
      await gameApi.end(id)
      reload()
    } catch (error) {
      console.error('Error ending game:', error)
    }
  }

  const recordScore = async (gameId, side, playerName) => {
    try {
      await gameApi.score(gameId, side, playerName, 1)
      reload()
    } catch (error) {
      console.error('Error recording goal:', error)
    }
  }

  const deleteGame = async (id) => {
    confirm({
      title: 'Delete Game',
      message: 'Are you sure you want to delete this game? This action cannot be undone.',
      confirmText: 'Delete',
      cancelText: 'Cancel',
      onConfirm: async () => {
        try {
          await gameApi.delete(id)
          reload()
        } catch (error) {
          console.error('Error deleting game:', error)
          alert({
            title: 'Error',
            message: 'Could not delete game. Please try again.',
          })
        }
      },
    })
  }

  return {
    createGame,
    startGame,
    pauseGame,
    resumeGame,
    endGame,
    recordScore,
    deleteGame,
  }
}
