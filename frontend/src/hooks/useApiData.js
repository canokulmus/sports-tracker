import { useState, useEffect, useCallback } from 'react'

export function useApiData(fetchFn, dependencies = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const reload = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchFn()
      setData(result)
    } catch (err) {
      setError(err)
      console.error('Data loading error:', err)
    } finally {
      setLoading(false)
    }
  }, [fetchFn])

  useEffect(() => {
    reload()
  }, dependencies)

  return { data, loading, error, reload }
}
