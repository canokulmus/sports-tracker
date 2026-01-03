// src/components/Cup/StandingsTable.jsx
import { colors } from '../../styles/colors'

function LeagueStandings({ standings }) {
  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th>#</th>
            <th>Team</th>
            <th>P</th>
            <th>W</th>
            <th>D</th>
            <th>L</th>
            <th>GF</th>
            <th>GA</th>
            <th>GD</th>
            <th>Pts</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((row, index) => (
            <tr key={row.team}>
              <td>
                <strong>{index + 1}</strong>
              </td>
              <td>
                <strong>{row.team}</strong>
              </td>
              <td>{row.played}</td>
              <td className="text-success">{row.won}</td>
              <td>{row.draw}</td>
              <td className="text-danger">{row.lost}</td>
              <td>{row.gf}</td>
              <td>{row.ga}</td>
              <td>{row.gf - row.ga}</td>
              <td>
                <strong>{row.points}</strong>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function GroupStandings({ standings }) {
  const groupNames = Object.keys(standings).sort()

  return (
    <div style={styles.groupContainer}>
      {groupNames.map((groupName) => (
        <div key={groupName} style={styles.groupCard}>
          <h4 style={styles.groupTitle}>Group {groupName}</h4>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Team</th>
                  <th>P</th>
                  <th>W</th>
                  <th>D</th>
                  <th>L</th>
                  <th>Pts</th>
                </tr>
              </thead>
              <tbody>
                {standings[groupName].map((row, index) => (
                  <tr key={row.team}>
                    <td>
                      <strong>{index + 1}</strong>
                    </td>
                    <td>
                      <strong>{row.team}</strong>
                    </td>
                    <td>{row.played}</td>
                    <td className="text-success">{row.won}</td>
                    <td>{row.draw}</td>
                    <td className="text-danger">{row.lost}</td>
                    <td>
                      <strong>{row.points}</strong>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  )
}

function StandingsTable({ standings, cupType }) {
  if (!standings || (Array.isArray(standings) && standings.length === 0)) {
    return (
      <div style={styles.empty}>
        <p>No standings yet</p>
      </div>
    )
  }

  // GROUP tournament has object with group names
  if (cupType === 'GROUP' && typeof standings === 'object' && !Array.isArray(standings)) {
    return <GroupStandings standings={standings} />
  }

  // LEAGUE tournament has array
  if (Array.isArray(standings)) {
    return <LeagueStandings standings={standings} />
  }

  return (
    <div style={styles.empty}>
      <p>Standings format not recognized</p>
    </div>
  )
}

const styles = {
  groupContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '20px',
  },
  groupCard: {
    background: colors.background.secondary,
    borderRadius: '12px',
    padding: '20px',
    border: `1px solid ${colors.ui.border}`,
  },
  groupTitle: {
    fontSize: '16px',
    fontWeight: '700',
    color: colors.brand.primary,
    marginBottom: '16px',
    paddingBottom: '12px',
    borderBottom: `1px solid ${colors.ui.borderDark}`,
  },
  empty: {
    textAlign: 'center',
    padding: '48px',
    color: colors.text.muted,
    background: colors.background.secondary,
    borderRadius: '12px',
    border: `1px solid ${colors.ui.border}`,
  },
}

export default StandingsTable
