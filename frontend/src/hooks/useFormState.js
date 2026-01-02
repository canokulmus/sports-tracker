import { useState, useCallback } from 'react'

export function useFormState(initialState) {
  const [formData, setFormData] = useState(initialState)

  const updateField = useCallback((field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }, [])

  const resetForm = useCallback(() => {
    setFormData(initialState)
  }, [initialState])

  const setForm = useCallback((data) => {
    setFormData(data)
  }, [])

  return { formData, updateField, resetForm, setForm }
}
