import { AlertTriangle, Info, CheckCircle, X } from 'lucide-react'
import { colors } from '../../styles/colors'
import { useDialog } from '../../context/DialogContext'
import { useMediaQuery, mediaQueries } from '../../utils/responsive'

function Dialog() {
  const { dialog } = useDialog()
  const isMobile = useMediaQuery(mediaQueries.mobile)

  if (!dialog) return null

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      if (dialog.type === 'confirm') {
        dialog.onCancel?.()
      } else {
        dialog.onClose?.()
      }
    }
  }

  const handleClose = () => {
    if (dialog.type === 'confirm') {
      dialog.onCancel?.()
    } else {
      dialog.onClose?.()
    }
  }

  const getIcon = () => {
    switch (dialog.type) {
      case 'confirm':
        return <AlertTriangle size={32} style={{ color: colors.state.warning }} />
      case 'alert':
        return <AlertTriangle size={32} style={{ color: colors.state.danger }} />
      case 'info':
        return <Info size={32} style={{ color: colors.ui.info }} />
      default:
        return <CheckCircle size={32} style={{ color: colors.state.success }} />
    }
  }

  const dialogStyle = {
    ...styles.dialog,
    ...(isMobile ? styles.dialogMobile : {}),
  }

  return (
    <div style={styles.backdrop} onClick={handleBackdropClick}>
      <div style={dialogStyle}>
        {isMobile && (
          <button
            className="dialog-close-btn"
            style={styles.closeBtn}
            onClick={handleClose}
            type="button"
            aria-label="Close"
          >
            <X size={20} />
          </button>
        )}

        <div style={styles.iconContainer}>{getIcon()}</div>

        {dialog.title && <h3 style={styles.title}>{dialog.title}</h3>}

        {dialog.message && <p style={styles.message}>{dialog.message}</p>}

        <div style={styles.actions}>
          {dialog.type === 'confirm' ? (
            <>
              <button
                className="btn btn-secondary"
                onClick={dialog.onCancel}
                style={styles.cancelBtn}
              >
                {dialog.cancelText}
              </button>
              <button
                className="btn btn-danger"
                onClick={dialog.onConfirm}
                style={styles.confirmBtn}
              >
                {dialog.confirmText}
              </button>
            </>
          ) : (
            <button
              className="btn btn-primary"
              onClick={dialog.onClose}
              style={styles.okBtn}
            >
              {dialog.buttonText}
            </button>
          )}
        </div>
      </div>

      {isMobile && (
        <style>{`
          .dialog-close-btn:hover {
            background: ${colors.background.primary};
            border-color: ${colors.ui.borderLight};
            color: ${colors.text.primary};
          }
        `}</style>
      )}
    </div>
  )
}

const styles = {
  backdrop: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: '20px',
  },
  dialog: {
    background: colors.background.secondary,
    borderRadius: '16px',
    padding: '32px',
    maxWidth: '480px',
    width: '100%',
    border: `1px solid ${colors.ui.border}`,
    boxShadow: `0 8px 32px ${colors.background.primary}80`,
    position: 'relative',
  },
  dialogMobile: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    maxWidth: '100%',
    borderRadius: 0,
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  closeBtn: {
    position: 'absolute',
    top: '16px',
    right: '16px',
    background: colors.background.tertiary,
    border: `1px solid ${colors.ui.border}`,
    borderRadius: '8px',
    width: '36px',
    height: '36px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    color: colors.text.secondary,
    transition: 'all 0.2s ease',
    zIndex: 1,
  },
  iconContainer: {
    display: 'flex',
    justifyContent: 'center',
    marginBottom: '16px',
  },
  title: {
    fontSize: '20px',
    fontWeight: '700',
    color: colors.text.primary,
    marginBottom: '12px',
    textAlign: 'center',
  },
  message: {
    fontSize: '15px',
    color: colors.text.secondary,
    marginBottom: '24px',
    textAlign: 'center',
    lineHeight: '1.5',
  },
  actions: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
  },
  cancelBtn: {
    minWidth: '100px',
  },
  confirmBtn: {
    minWidth: '100px',
  },
  okBtn: {
    minWidth: '120px',
  },
}

export default Dialog
