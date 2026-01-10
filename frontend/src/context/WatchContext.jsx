import { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { onGameNotification, watchApi } from '../services/api'
import { useUser } from './UserContext'

const WatchContext = createContext(null)

export function WatchProvider({ children }) {
  const [watchedGames, setWatchedGames] = useState([])
  const [watchedCups, setWatchedCups] = useState([])
  const [autoWatchedGames, setAutoWatchedGames] = useState({}) // Map of gameId -> cupId for auto-watched games
  const [notifications, setNotifications] = useState([])
  const { user } = useUser()

  // Load watched games and cups from server on mount
  useEffect(() => {
    console.log('[WatchContext] User state changed:', user)
    if (!user) {
      setWatchedGames([])
      setWatchedCups([])
      return
    }

    const loadWatchedItems = async () => {
      try {
        const games = await watchApi.getWatchedGames()
        const gameIds = games.map(g => g.id)
        setWatchedGames(gameIds)
        console.log('[WatchContext] Loaded watched games from server:', gameIds)

        // Build autoWatchedGames map from the response
        const autoWatchedMap = {}
        games.forEach(game => {
          if (game.autoWatchedFromCup) {
            autoWatchedMap[game.id] = game.autoWatchedFromCup
          }
        })
        setAutoWatchedGames(autoWatchedMap)
        console.log('[WatchContext] Auto-watched games:', autoWatchedMap)

        const cups = await watchApi.getWatchedCups()
        const cupIds = cups.map(c => c.id)
        setWatchedCups(cupIds)
        console.log('[WatchContext] Loaded watched cups from server:', cupIds)
      } catch (error) {
        console.error('[WatchContext] Failed to load watched items:', error)
        // Initialize with empty arrays on error
        setWatchedGames([])
        setWatchedCups([])
        setAutoWatchedGames({})
      }
    }

    loadWatchedItems()
  }, [user])

  useEffect(() => {
    const unsubscribe = onGameNotification((notification) => {
      console.log('[WatchContext] Received notification:', notification)

      if (notification.type === 'NOTIFICATION' && notification.game_id) {
        const gameId = notification.game_id
        console.log('[WatchContext] Game ID:', gameId, 'Watched games:', watchedGames, 'Watched cups:', watchedCups)

        // Check if this game is watched directly OR part of a watched cup
        const isGameWatched = watchedGames.includes(gameId)
        const isCupWatched = watchedCups.length > 0 // If user watches any cup, show all game notifications from watched cups

        if (isGameWatched || isCupWatched) {
          const message = `${notification.home} vs ${notification.away}: ${notification.score.home}-${notification.score.away} (${notification.state})`
          console.log('[WatchContext] Creating notification:', message)

          const newNotification = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            gameId: gameId,
            message: message,
            type: isGameWatched ? 'game_update' : 'cup_game_update'
          }

          setNotifications((prev) => [newNotification, ...prev].slice(0, 50))
        } else {
          console.log('[WatchContext] Game not watched (neither directly nor via cup), ignoring notification')
        }
      }
    })

    return () => {
      if (unsubscribe) unsubscribe()
    }
  }, [watchedGames, watchedCups])

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

  const watchCup = useCallback(async (cupId) => {
    try {
      const response = await watchApi.watchCup(cupId)
      setWatchedCups((prev) => {
        if (prev.includes(cupId)) return prev
        return [...prev, cupId]
      })

      // If backend returned auto_watched_games, update our state
      if (response && response.auto_watched_games) {
        const newAutoWatchedGames = {}
        response.auto_watched_games.forEach(gameId => {
          newAutoWatchedGames[gameId] = cupId
        })
        setAutoWatchedGames(prev => ({ ...prev, ...newAutoWatchedGames }))
        setWatchedGames(prev => [...new Set([...prev, ...response.auto_watched_games])])
        console.log('[WatchContext] Auto-watched games from cup:', response.auto_watched_games)
      }
    } catch (error) {
      console.error('Failed to watch cup:', error)
      throw error
    }
  }, [])

  const unwatchCup = useCallback(async (cupId) => {
    try {
      await watchApi.unwatchCup(cupId)
      setWatchedCups((prev) => prev.filter((id) => id !== cupId))

      // Remove all auto-watched games from this cup
      setAutoWatchedGames(prev => {
        const gamesToRemove = Object.keys(prev).filter(gameId => prev[gameId] === cupId)
        const newAutoWatched = { ...prev }
        gamesToRemove.forEach(gameId => delete newAutoWatched[gameId])

        // Also remove these games from watchedGames
        setWatchedGames(watchedPrev => watchedPrev.filter(id => !gamesToRemove.includes(id.toString())))

        return newAutoWatched
      })
    } catch (error) {
      console.error('Failed to unwatch cup:', error)
      throw error
    }
  }, [])

  const isWatchingCup = useCallback((cupId) => {
    return watchedCups.includes(cupId)
  }, [watchedCups])

  const toggleWatchCup = useCallback((cupId) => {
    if (isWatchingCup(cupId)) {
      unwatchCup(cupId)
    } else {
      watchCup(cupId)
    }
  }, [isWatchingCup, watchCup, unwatchCup])

  const isGameAutoWatched = useCallback((gameId) => {
    return gameId in autoWatchedGames
  }, [autoWatchedGames])

  const getAutoWatchedCupId = useCallback((gameId) => {
    return autoWatchedGames[gameId]
  }, [autoWatchedGames])

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
    watchedCups,
    watchCup,
    unwatchCup,
    isWatchingCup,
    toggleWatchCup,
    isGameAutoWatched,
    getAutoWatchedCupId,
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
