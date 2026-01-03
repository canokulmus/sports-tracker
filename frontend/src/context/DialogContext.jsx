import { createContext, useContext, useState } from 'react'

const DialogContext = createContext()

export function DialogProvider({ children }) {
  const [dialog, setDialog] = useState(null)

  const showDialog = (config) => {
    setDialog(config)
  }

  const hideDialog = () => {
    setDialog(null)
  }

  const confirm = ({ title, message, onConfirm, confirmText = 'Confirm', cancelText = 'Cancel' }) => {
    showDialog({
      type: 'confirm',
      title,
      message,
      confirmText,
      cancelText,
      onConfirm: () => {
        onConfirm?.()
        hideDialog()
      },
      onCancel: hideDialog,
    })
  }

  const alert = ({ title, message, buttonText = 'OK' }) => {
    showDialog({
      type: 'alert',
      title,
      message,
      buttonText,
      onClose: hideDialog,
    })
  }

  const info = ({ title, message, buttonText = 'Got it' }) => {
    showDialog({
      type: 'info',
      title,
      message,
      buttonText,
      onClose: hideDialog,
    })
  }

  return (
    <DialogContext.Provider value={{ dialog, showDialog, hideDialog, confirm, alert, info }}>
      {children}
    </DialogContext.Provider>
  )
}

export function useDialog() {
  const context = useContext(DialogContext)
  if (!context) {
    throw new Error('useDialog must be used within DialogProvider')
  }
  return context
}
