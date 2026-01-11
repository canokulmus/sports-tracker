import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Trophy, Calendar } from 'lucide-react'
import { cupApi, onGameNotification } from '../services/api'
import { colors } from '../styles/colors'
import { Loader } from '../components/Loader'
import StandingsTable from '../components/Cup/StandingsTable'
import GameTree from '../components/Cup/GameTree'
import GameCard from '../components/Game/GameCard'
import WatchButton from '../components/WatchButton'
import { useWatch } from '../context/WatchContext'

function CupDetail() {
  const { cupId } = useParams()
  const navigate = useNavigate()
  const { isWatchingCup, toggleWatchCup } = useWatch()

  const [cup, setCup] = useState(null)
  const [standings, setStandings] = useState(null)
  const [gameTree, setGameTree] = useState(null)
  const [fixtures, setFixtures] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('')

  useEffect(() => {
    loadCupData()
  }, [cupId])

  useEffect(() => {
    const unsubscribe = onGameNotification((notification) => {
      if (notification.type === 'NOTIFICATION' && notification.game_id) {
        const gameInCup = fixtures.some(game => game.id === notification.game_id)
        if (gameInCup) {
          console.log('[CupDetail] Received update for game in this cup, reloading...')
          loadCupData()
        }
      }
    })

    return () => {
      if (unsubscribe) unsubscribe()
    }
  }, [cupId, fixtures])

  const loadCupData = async () => {
    try {
      setLoading(true)
      const cupData = await cupApi.getById(parseInt(cupId))
      setCup(cupData)

      if (cupData.type === 'ELIMINATION' || cupData.type === 'ELIMINATION2') {
        setActiveTab('bracket')
      } else {
        setActiveTab('standings')
      }

      if (cupData.type !== 'ELIMINATION' && cupData.type !== 'ELIMINATION2') {
        const standingsData = await cupApi.getStandings(parseInt(cupId))
        setStandings(standingsData)
      }

      const cupGames = await cupApi.getCupGames(parseInt(cupId))
      setFixtures(cupGames)

      const needsGameTree = ['GROUP', 'GROUP2', 'ELIMINATION', 'ELIMINATION2'].includes(cupData.type)
      if (needsGameTree) {
        try {
          const gameTreeData = await cupApi.getGameTree(parseInt(cupId))
          setGameTree(gameTreeData)
        } catch (err) {
          console.log('GameTree not available yet:', err)
          setGameTree(null)
        }
      }
    } catch (error) {
      console.error('Error loading cup data:', error)
      alert('Could not load tournament details')
      navigate('/cups')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Loader text="Loading tournament details..." />
  }

  if (!cup) {
    return (
      <div style={styles.empty}>
        <p>Tournament not found</p>
      </div>
    )
  }

  return (
    <div>
      <div style={styles.header}>
        <button
          className="btn btn-secondary"
          onClick={() => navigate('/cups')}
          style={styles.backBtn}
        >
          <ArrowLeft size={18} />
          Back
        </button>

        <div style={styles.headerInfo}>
          <div style={styles.titleRow}>
            <Trophy size={28} color={colors.brand.primary} />
            <h1 className="page-title" style={{ marginBottom: 0 }}>{cup.name}</h1>
            <WatchButton
              isWatching={isWatchingCup(parseInt(cupId))}
              onToggle={() => toggleWatchCup(parseInt(cupId))}
              variant="default"
            />
          </div>
          <div style={styles.meta}>
            <span
              className="badge"
              style={{
                backgroundColor: getTournamentColor(cup.type),
                color: colors.quickColors.white,
              }}
            >
              {cup.type}
            </span>
            <span className="text-muted">
              {cup.teams.length} teams • {cup.gameCount} games
            </span>
          </div>
        </div>
      </div>

      <div style={styles.tabs}>
        {cup.type !== 'ELIMINATION' && cup.type !== 'ELIMINATION2' && (
          <button
            style={{
              ...styles.tab,
              ...(activeTab === 'standings' ? styles.tabActive : {}),
            }}
            onClick={() => setActiveTab('standings')}
          >
            Standings
          </button>
        )}

        {(cup.type === 'ELIMINATION' || cup.type === 'ELIMINATION2') && (
          <button
            style={{
              ...styles.tab,
              ...(activeTab === 'bracket' ? styles.tabActive : {}),
            }}
            onClick={() => setActiveTab('bracket')}
          >
            <Trophy size={16} style={{ marginRight: '6px' }} />
            Knockout Stages
          </button>
        )}

        <button
          style={{
            ...styles.tab,
            ...(activeTab === 'fixtures' ? styles.tabActive : {}),
          }}
          onClick={() => setActiveTab('fixtures')}
        >
          <Calendar size={16} style={{ marginRight: '6px' }} />
          Fixtures
        </button>

        {(cup.type === 'GROUP' || cup.type === 'GROUP2') && (
          <button
            style={{
              ...styles.tab,
              ...(activeTab === 'playoffs' ? styles.tabActive : {}),
            }}
            onClick={() => setActiveTab('playoffs')}
          >
            Playoff Stage
          </button>
        )}
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        {activeTab === 'standings' && (
          <div>
            <h3 className="card-title mb-4">Standings</h3>
            <StandingsTable standings={standings} cupType={cup.type} />
          </div>
        )}

        {activeTab === 'bracket' && (
          <div>
            <h3 className="card-title mb-4">Knockout Stages</h3>
            {gameTree ? (
              <GameTree gameTree={gameTree} cupType={cup.type} />
            ) : (
              <div style={styles.emptyFixtures}>
                <Trophy size={48} color={colors.text.muted} style={{ opacity: 0.3 }} />
                <p className="text-muted">Bracket not available yet</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'fixtures' && (
          <div>
            <h3 className="card-title mb-4">Fixtures ({fixtures.length} games)</h3>
            {fixtures.length === 0 ? (
              <div style={styles.emptyFixtures}>
                <Calendar size={48} color={colors.text.muted} style={{ opacity: 0.3 }} />
                <p className="text-muted">No games scheduled yet</p>
              </div>
            ) : (
              <div style={styles.fixturesGrid}>
                {fixtures.map((game) => (
                  <GameCard
                    key={game.id}
                    game={game}
                    variant="compact"
                    onClick={(gameId) => navigate(`/games/${gameId}`)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'playoffs' && (
          <div>
            <h3 className="card-title mb-4">Playoff Stage</h3>
            {gameTree ? (
              <GameTree gameTree={gameTree} cupType={cup.type} playoffOnly={true} />
            ) : (
              <div style={styles.emptyFixtures}>
                <Trophy size={48} color={colors.text.muted} style={{ opacity: 0.3 }} />
                <p className="text-muted">Playoff bracket will appear after group stage is complete</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function getTournamentColor(type) {
  const colorMap = {
    LEAGUE: colors.tournament.league,
    LEAGUE2: colors.tournament.league,
    ELIMINATION: colors.tournament.elimination,
    ELIMINATION2: colors.tournament.elimination,
    GROUP: colors.tournament.group,
    GROUP2: colors.tournament.group,
  }
  return colorMap[type] || colors.text.muted
}

const styles = {
  header: {
    display: 'flex',
    gap: '20px',
    alignItems: 'flex-start',
    marginBottom: '24px',
  },
  backBtn: {
    flexShrink: 0,
  },
  headerInfo: {
    flex: 1,
  },
  titleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px',
  },
  meta: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  tabs: {
    display: 'flex',
    gap: '8px',
    borderBottom: `2px solid ${colors.ui.border}`,
  },
  tab: {
    padding: '12px 24px',
    background: 'transparent',
    border: 'none',
    borderBottom: '2px solid transparent',
    color: colors.text.muted,
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    marginBottom: '-2px',
    outline: 'none',
    display: 'flex',
    alignItems: 'center',
  },
  tabActive: {
    color: colors.brand.primary,
    borderBottomColor: colors.brand.primary,
  },
  empty: {
    textAlign: 'center',
    padding: '48px',
    color: colors.text.muted,
  },
  emptyFixtures: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '60px 24px',
    gap: '16px',
  },
  fixturesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '16px',
  },
}

export default CupDetail
