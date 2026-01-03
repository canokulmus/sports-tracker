import { useState } from 'react'
import { Plus, Trash2, Tag } from 'lucide-react'
import { colors } from '../../styles/colors'

function CustomFieldsManager({ fields = {}, onAddField, onDeleteField }) {
  const [newField, setNewField] = useState({ key: '', value: '' })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!newField.key.trim() || !newField.value.trim()) return

    onAddField(newField.key.trim(), newField.value.trim())
    setNewField({ key: '', value: '' })
  }

  const fieldEntries = Object.entries(fields).filter(
    ([key]) => !['id', 'name', 'players'].includes(key)
  )

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <Tag size={18} style={{ color: colors.ui.info }} />
        <h4 style={styles.title}>Custom Fields</h4>
      </div>

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.inputRow}>
          <input
            type="text"
            className="form-input"
            placeholder="Field name (e.g. city)"
            value={newField.key}
            onChange={(e) => setNewField({ ...newField, key: e.target.value })}
            style={styles.input}
          />
          <input
            type="text"
            className="form-input"
            placeholder="Value (e.g. Istanbul)"
            value={newField.value}
            onChange={(e) => setNewField({ ...newField, value: e.target.value })}
            style={styles.input}
          />
          <button type="submit" className="btn btn-success btn-sm">
            <Plus size={16} />
          </button>
        </div>
      </form>

      {fieldEntries.length === 0 ? (
        <p style={styles.emptyText}>No custom fields added yet</p>
      ) : (
        <div style={styles.fieldsList}>
          {fieldEntries.map(([key, value]) => (
            <div key={key} style={styles.fieldItem}>
              <div style={styles.fieldContent}>
                <span style={styles.fieldKey}>{key}:</span>
                <span style={styles.fieldValue}>{String(value)}</span>
              </div>
              <button
                className="btn btn-danger btn-sm"
                onClick={() => onDeleteField(key)}
                style={styles.deleteBtn}
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const styles = {
  container: {
    marginTop: '24px',
    padding: '16px',
    backgroundColor: colors.background.tertiary,
    borderRadius: '8px',
    border: `1px solid ${colors.ui.borderSubtle}`,
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '16px',
  },
  title: {
    margin: 0,
    fontSize: '16px',
    fontWeight: '600',
    color: colors.text.primary,
  },
  form: {
    marginBottom: '16px',
  },
  inputRow: {
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
  },
  input: {
    flex: 1,
  },
  emptyText: {
    color: colors.text.muted,
    fontSize: '14px',
    margin: 0,
    textAlign: 'center',
    padding: '12px 0',
  },
  fieldsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  fieldItem: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px 12px',
    backgroundColor: colors.background.secondary,
    borderRadius: '6px',
    border: `1px solid ${colors.ui.borderSubtle}`,
  },
  fieldContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flex: 1,
  },
  fieldKey: {
    color: colors.ui.info,
    fontWeight: '600',
    fontSize: '14px',
  },
  fieldValue: {
    color: colors.text.primary,
    fontSize: '14px',
  },
  deleteBtn: {
    marginLeft: '8px',
  },
}

export default CustomFieldsManager
