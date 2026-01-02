import { useState, useEffect, useRef, useCallback } from 'react'

export function useWebSocket(url, options = {}) {
  const [data, setData] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)

  const {
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnect = true,
    reconnectInterval = 3000,
  } = options

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = (event) => {
        setIsConnected(true)
        setError(null)
        onOpen?.(event)
      }

      ws.onmessage = (event) => {
        try {
          const parsedData = JSON.parse(event.data)
          setData(parsedData)
          onMessage?.(parsedData, event)
        } catch (err) {
          console.error('WebSocket message parse error:', err)
        }
      }

      ws.onerror = (event) => {
        setError(event)
        onError?.(event)
      }

      ws.onclose = (event) => {
        setIsConnected(false)
        onClose?.(event)

        if (reconnect && !event.wasClean) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        }
      }
    } catch (err) {
      setError(err)
      console.error('WebSocket connection error:', err)
    }
  }, [url, onMessage, onOpen, onClose, onError, reconnect, reconnectInterval])

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  const send = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const payload = typeof message === 'string' ? message : JSON.stringify(message)
      wsRef.current.send(payload)
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
    }
  }, [])

  return { data, isConnected, error, send, disconnect, reconnect: connect }
}
