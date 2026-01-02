import { useState, useCallback } from 'react'

export function useSelection(initialValue = null) {
  const [selected, setSelected] = useState(initialValue)

  const select = useCallback((item) => setSelected(item), [])
  const clear = useCallback(() => setSelected(null), [])
  const toggle = useCallback(
    (item, compareFn = (a, b) => a === b) => {
      setSelected((prev) => (compareFn(prev, item) ? null : item))
    },
    []
  )

  return { selected, select, clear, toggle }
}

export function useMultiSelection(initialValue = []) {
  const [selected, setSelected] = useState(initialValue)

  const toggleItem = useCallback((item, compareFn = (a, b) => a === b) => {
    setSelected((prev) => {
      const exists = prev.some((x) => compareFn(x, item))
      return exists ? prev.filter((x) => !compareFn(x, item)) : [...prev, item]
    })
  }, [])

  const selectAll = useCallback((items) => setSelected(items), [])
  const clearAll = useCallback(() => setSelected([]), [])
  const isSelected = useCallback(
    (item, compareFn = (a, b) => a === b) => {
      return selected.some((x) => compareFn(x, item))
    },
    [selected]
  )

  return { selected, toggleItem, selectAll, clearAll, isSelected }
}
