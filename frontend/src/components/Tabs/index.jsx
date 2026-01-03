import { colors } from '../../styles/colors'

function Tabs({ tabs, activeTab, onTabChange }) {
  return (
    <div style={styles.container}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          style={{
            ...styles.tab,
            ...(activeTab === tab.id ? styles.tabActive : {}),
          }}
          onClick={() => onTabChange(tab.id)}
          type="button"
        >
          {tab.label}
          {tab.count !== undefined && (
            <span style={{
              ...styles.count,
              ...(activeTab === tab.id ? styles.countActive : {}),
            }}>
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    gap: '8px',
    borderBottom: `1px solid ${colors.ui.border}`,
    marginBottom: '24px',
    overflowX: 'auto',
    paddingBottom: '2px',
  },
  tab: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 20px',
    background: 'transparent',
    border: 'none',
    borderBottom: '2px solid transparent',
    color: colors.text.secondary,
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    whiteSpace: 'nowrap',
    position: 'relative',
    bottom: '-2px',
  },
  tabActive: {
    color: colors.brand.primary,
    borderBottomColor: colors.brand.primary,
    background: `${colors.brand.primary}05`,
  },
  count: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: '20px',
    height: '20px',
    padding: '0 6px',
    borderRadius: '10px',
    fontSize: '11px',
    fontWeight: '600',
    background: colors.background.tertiary,
    color: colors.text.muted,
  },
  countActive: {
    background: `${colors.brand.primary}20`,
    color: colors.brand.primary,
  },
}

export default Tabs
