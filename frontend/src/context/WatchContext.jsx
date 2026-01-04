import { createContext, useContext, useState, useCallback, useEffect } from 'react'

const WatchContext = createContext(null)

export function WatchProvider({ children }) {
  const [watchedGames, setWatchedGames] = useState(() => {
    const saved = localStorage.getItem('watchedGames')
    return saved ? JSON.parse(saved) : []
  })

  const [notifications, setNotifications] = useState(() => {
    const saved = localStorage.getItem('watchNotifications')
    return saved ? JSON.parse(saved) : []
  })

  useEffect(() => {
    localStorage.setItem('watchedGames', JSON.stringify(watchedGames))
  }, [watchedGames])

  useEffect(() => {
    localStorage.setItem('watchNotifications', JSON.stringify(notifications))
  }, [notifications])

  const watchGame = useCallback((gameId) => {
    setWatchedGames((prev) => {
      if (prev.includes(gameId)) return prev
      return [...prev, gameId]
    })
  }, [])

  const unwatchGame = useCallback((gameId) => {
    setWatchedGames((prev) => prev.filter((id) => id !== gameId))
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
    localStorage.removeItem('watchNotifications')
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
