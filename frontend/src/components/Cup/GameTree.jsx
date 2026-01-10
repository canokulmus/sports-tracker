// src/components/Cup/GameTree.jsx
import { colors } from '../../styles/colors'
import StatusBadge from '../Game/StatusBadge'

function BracketMatch({ match }) {
  const hasScore = match.score !== null && match.score !== undefined
  const isPlaceholder = match.home?.startsWith('Winner') || match.away?.startsWith('Winner')

  return (
    <div style={styles.match}>
      <div style={styles.matchHeader}>
        <StatusBadge state={match.state} />
        <span style={styles.matchId}>#{match.game_id}</span>
      </div>

      <div style={styles.teams}>
        {/* Home Team */}
        <div style={{
          ...styles.team,
          ...(hasScore && match.score.home > match.score.away ? styles.teamWinner : {}),
        }}>
          <span style={isPlaceholder ? styles.placeholderText : styles.teamName}>
            {match.home}
          </span>
          {hasScore && (
            <span style={styles.score}>{match.score.home}</span>
          )}
        </div>

        {/* Away Team */}
        <div style={{
          ...styles.team,
          ...(hasScore && match.score.away > match.score.home ? styles.teamWinner : {}),
        }}>
          <span style={isPlaceholder ? styles.placeholderText : styles.teamName}>
            {match.away}
          </span>
          {hasScore && (
            <span style={styles.score}>{match.score.away}</span>
          )}
        </div>
      </div>

      <div style={styles.datetime}>{match.datetime}</div>
    </div>
  )
}

function EliminationBracket({ gameTree }) {
  const rounds = Object.keys(gameTree)

  return (
    <div style={styles.bracket}>
      {rounds.map((roundName) => (
        <div key={roundName} style={styles.round}>
          <h4 style={styles.roundTitle}>{roundName}</h4>
          <div style={styles.matches}>
            {gameTree[roundName].map((match) => (
              <BracketMatch key={match.game_id} match={match} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function GroupStage({ groups }) {
  const groupNames = Object.keys(groups)

  return (
    <div style={styles.groupStage}>
      <h3 style={styles.sectionTitle}>Group Stage</h3>
      {groupNames.map((groupName) => (
        <div key={groupName} style={styles.groupSection}>
          <h4 style={styles.groupTitle}>Group {groupName}</h4>
          <div style={styles.groupMatches}>
            {groups[groupName].map((match) => (
              <BracketMatch key={match.game_id} match={match} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function GameTree({ gameTree, cupType, playoffOnly = false }) {
  if (!gameTree) {
    return (
      <div style={styles.empty}>
        <p>GameTree data not found</p>
      </div>
    )
  }

  // GROUP tournament: Groups + Playoffs
  if (cupType === 'GROUP') {
    // If playoffOnly is true, only show the playoff bracket
    if (playoffOnly) {
      if (gameTree.Playoffs && Object.keys(gameTree.Playoffs).length > 0) {
        return (
          <div style={styles.container}>
            <EliminationBracket gameTree={gameTree.Playoffs} />
          </div>
        )
      }
      return (
        <div style={styles.empty}>
          <p>Playoff bracket will appear after group stage is complete</p>
        </div>
      )
    }

    // Show both groups and playoffs
    return (
      <div style={styles.container}>
        {gameTree.Groups && <GroupStage groups={gameTree.Groups} />}

        {gameTree.Playoffs && Object.keys(gameTree.Playoffs).length > 0 && (
          <div style={styles.playoffSection}>
            <h3 style={styles.sectionTitle}>Playoff Stage</h3>
            <EliminationBracket gameTree={gameTree.Playoffs} />
          </div>
        )}
      </div>
    )
  }

  // ELIMINATION tournament: Just the bracket
  return (
    <div style={styles.container}>
      <EliminationBracket gameTree={gameTree} />
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: '700',
    color: colors.text.primary,
    marginBottom: '20px',
    borderBottom: `2px solid ${colors.ui.border}`,
    paddingBottom: '12px',
  },
  groupStage: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  groupSection: {
    background: colors.background.secondary,
    borderRadius: '12px',
    padding: '20px',
    border: `1px solid ${colors.ui.border}`,
  },
  groupTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: colors.brand.primary,
    marginBottom: '16px',
  },
  groupMatches: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  playoffSection: {
    marginTop: '24px',
  },
  bracket: {
    display: 'flex',
    gap: '24px',
    overflowX: 'auto',
    paddingBottom: '16px',
  },
  round: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    minWidth: '280px',
  },
  roundTitle: {
    fontSize: '16px',
    fontWeight: '700',
    color: colors.brand.primary,
    textAlign: 'center',
    padding: '12px',
    background: colors.background.tertiary,
    borderRadius: '8px',
    border: `1px solid ${colors.ui.border}`,
  },
  matches: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  match: {
    background: colors.background.secondary,
    borderRadius: '12px',
    padding: '16px',
    border: `1px solid ${colors.ui.border}`,
    transition: 'all 0.2s ease',
  },
  matchHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },
  matchId: {
    fontSize: '12px',
    color: colors.text.muted,
    fontWeight: '500',
  },
  teams: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    marginBottom: '12px',
  },
  team: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 12px',
    background: colors.background.tertiary,
    borderRadius: '8px',
    border: `1px solid ${colors.ui.borderDark}`,
    transition: 'all 0.2s ease',
  },
  teamWinner: {
    background: `${colors.state.success}10`,
    borderColor: `${colors.state.success}40`,
  },
  teamName: {
    fontSize: '14px',
    fontWeight: '600',
    color: colors.text.primary,
  },
  placeholderText: {
    fontSize: '13px',
    fontWeight: '500',
    color: colors.text.muted,
    fontStyle: 'italic',
  },
  score: {
    fontSize: '18px',
    fontWeight: '700',
    color: colors.brand.primary,
    minWidth: '24px',
    textAlign: 'right',
  },
  datetime: {
    fontSize: '12px',
    color: colors.text.muted,
    textAlign: 'center',
  },
  empty: {
    textAlign: 'center',
    padding: '48px',
    color: colors.text.muted,
  },
}

export default GameTree
