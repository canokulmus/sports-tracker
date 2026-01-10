import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { onGameNotification, watchApi } from '../services/api'

const WatchContext = createContext(null)

export function WatchProvider({ children }) {
  const [watchedGames, setWatchedGames] = useState([])
  const [notifications, setNotifications] = useState([])

  // Load watched games from server on mount
  useEffect(() => {
    const loadWatchedGames = async () => {
      try {
        const games = await watchApi.getWatchedGames()
        const gameIds = games.map(g => g.id)
        setWatchedGames(gameIds)
        console.log('[WatchContext] Loaded watched games from server:', gameIds)
      } catch (error) {
        console.error('[WatchContext] Failed to load watched games:', error)
        // Initialize with empty array on error
        setWatchedGames([])
      }
    }

    // Small delay to ensure WebSocket is connected
    setTimeout(loadWatchedGames, 1000)
  }, []) // Only run once on mount

  useEffect(() => {
    const unsubscribe = onGameNotification((notification) => {
      console.log('[WatchContext] Received notification:', notification)

      if (notification.type === 'NOTIFICATION' && notification.game_id) {
        const gameId = notification.game_id
        console.log('[WatchContext] Game ID:', gameId, 'Watched games:', watchedGames)

        if (watchedGames.includes(gameId)) {
          const message = `${notification.home} vs ${notification.away}: ${notification.score.home}-${notification.score.away} (${notification.state})`
          console.log('[WatchContext] Creating notification:', message)

          const newNotification = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            gameId: gameId,
            message: message,
            type: 'game_update'
          }

          setNotifications((prev) => [newNotification, ...prev].slice(0, 50))
        } else {
          console.log('[WatchContext] Game not watched, ignoring notification')
        }
      }
    })

    return () => {
      if (unsubscribe) unsubscribe()
    }
  }, [watchedGames])

  const watchGame = useCallback(async (gameId) => {
    try {
      // Send WATCH command to backend
      await watchApi.watch(gameId)

      // Update local state
      setWatchedGames((prev) => {
        if (prev.includes(gameId)) return prev
        return [...prev, gameId]
      })
    } catch (error) {
      console.error('Failed to watch game:', error)
      throw error
    }
  }, [])

  const unwatchGame = useCallback(async (gameId) => {
    try {
      // Send UNWATCH command to backend
      await watchApi.unwatch(gameId)

      // Update local state
      setWatchedGames((prev) => prev.filter((id) => id !== gameId))
    } catch (error) {
      console.error('Failed to unwatch game:', error)
      throw error
    }
  }, [])

  const isWatching = useCallback((gameId) => {
    return watchedGames.includes(gameId)
  }, [watchedGames])

  const toggleWatch = useCallback((gameId) => {
    if (isWatching(gameId)) {
      unwatchGame(gameId)
    } else {
      watchGame(gameId)
    }
  }, [isWatching, watchGame, unwatchGame])

  const addNotification = useCallback((notification) => {
    const newNotification = {
      ...notification,
      id: Date.now(),
      timestamp: new Date().toISOString(),
    }
    setNotifications((prev) => [newNotification, ...prev].slice(0, 50))
  }, [])

  const clearNotifications = useCallback(() => {
    setNotifications([])
  }, [])

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  const value = {
    watchedGames,
    watchGame,
    unwatchGame,
    isWatching,
    toggleWatch,
    notifications,
    addNotification,
    clearNotifications,
    removeNotification,
  }

  return <WatchContext.Provider value={value}>{children}</WatchContext.Provider>
}

export function useWatch() {
  const context = useContext(WatchContext)
  if (!context) {
    throw new Error('useWatch must be used within WatchProvider')
  }
  return context
}
