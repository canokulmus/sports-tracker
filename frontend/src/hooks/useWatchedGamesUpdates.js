import { useEffect, useRef } from 'react'
import { useWatch } from '../context/WatchContext'
import { simulateGameUpdate } from '../services/api'

export function useWatchedGamesUpdates(onUpdate, enabled = true, interval = 10000) {
  const { watchedGames, addNotification } = useWatch()
  const intervalRef = useRef(null)
  const refreshCountRef = useRef(0)

  useEffect(() => {
    if (!enabled || watchedGames.length === 0) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      return
    }

    console.log('[Watch Updates] Starting simulation for', watchedGames.length, 'games')

    intervalRef.current = setInterval(() => {
      if (watchedGames.length === 0) return

      const randomGameId = watchedGames[Math.floor(Math.random() * watchedGames.length)]
      const updateType = Math.random() > 0.7 ? 'state' : 'score'

      console.log('[Watch Updates] Simulating update for game', randomGameId, 'type:', updateType)

      const event = simulateGameUpdate(randomGameId, updateType)

      console.log('[Watch Updates] Event returned:', event)

      if (event) {
        let message = ''
        if (event.type === 'score') {
          message = `${event.side === 'home' ? 'Home' : 'Away'} team scored! New score: ${event.score.home} - ${event.score.away}`
        } else if (event.type === 'state') {
          message = `Game state changed from ${event.oldState} to ${event.newState}`
        }

        console.log('[Watch Updates] Notification:', message)

        addNotification({
          gameId: event.gameId,
          type: event.type,
          message,
        })

        refreshCountRef.current += 1
        if (refreshCountRef.current % 3 === 0) {
          console.log('[Watch Updates] Refreshing data...')
          onUpdate?.()
        }
      } else {
        console.log('[Watch Updates] No event returned - game probably not RUNNING')
      }
    }, interval)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [enabled, watchedGames, interval, addNotification, onUpdate])
}
