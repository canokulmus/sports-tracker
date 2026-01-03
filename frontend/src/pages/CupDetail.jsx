// src/pages/CupDetail.jsx
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Trophy } from 'lucide-react'
import { cupApi } from '../services/api'
import { colors } from '../styles/colors'
import { Loader } from '../components/Loader'
import StandingsTable from '../components/Cup/StandingsTable'
import GameTree from '../components/Cup/GameTree'

function CupDetail() {
  const { cupId } = useParams()
  const navigate = useNavigate()

  const [cup, setCup] = useState(null)
  const [standings, setStandings] = useState(null)
  const [gameTree, setGameTree] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('standings')

  useEffect(() => {
    loadCupData()
  }, [cupId])

  const loadCupData = async () => {
    try {
      setLoading(true)
      const cupData = await cupApi.getById(parseInt(cupId))
      setCup(cupData)

      // Load standings
      const standingsData = await cupApi.getStandings(parseInt(cupId))
      setStandings(standingsData)

      // Load GameTree if not LEAGUE
      if (cupData.type !== 'LEAGUE') {
        try {
          const gameTreeData = await cupApi.getGameTree(parseInt(cupId))
          setGameTree(gameTreeData)
          setActiveTab('gametree') // Default to GameTree for ELIMINATION/GROUP
        } catch (err) {
          console.log('GameTree not available:', err)
        }
      }
    } catch (error) {
      console.error('Error loading cup data:', error)
      alert('Turnuva bilgileri yüklenemedi')
      navigate('/cups')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Loader text="Turnuva detayları yükleniyor..." />
  }

  if (!cup) {
    return (
      <div style={styles.empty}>
        <p>Turnuva bulunamadı</p>
      </div>
    )
  }

  const hasGameTree = cup.type !== 'LEAGUE'

  return (
    <div>
      {/* Header with back button */}
      <div style={styles.header}>
        <button
          className="btn btn-secondary"
          onClick={() => navigate('/cups')}
          style={styles.backBtn}
        >
          <ArrowLeft size={18} />
          Geri
        </button>

        <div style={styles.headerInfo}>
          <div style={styles.titleRow}>
            <Trophy size={28} color={colors.brand.primary} />
            <h1 className="page-title" style={{ marginBottom: 0 }}>{cup.name}</h1>
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
              {cup.teams.length} takım • {cup.gameCount} maç
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={styles.tabs}>
        <button
          style={{
            ...styles.tab,
            ...(activeTab === 'standings' ? styles.tabActive : {}),
          }}
          onClick={() => setActiveTab('standings')}
        >
          Puan Durumu
        </button>
        {hasGameTree && (
          <button
            style={{
              ...styles.tab,
              ...(activeTab === 'gametree' ? styles.tabActive : {}),
            }}
            onClick={() => setActiveTab('gametree')}
          >
            Maç Ağacı
          </button>
        )}
      </div>

      {/* Content */}
      <div className="card" style={{ marginTop: '24px' }}>
        {activeTab === 'standings' && (
          <div>
            <h3 className="card-title mb-4">Puan Durumu</h3>
            <StandingsTable standings={standings} cupType={cup.type} />
          </div>
        )}

        {activeTab === 'gametree' && (
          <div>
            <h3 className="card-title mb-4">Maç Ağacı</h3>
            <GameTree gameTree={gameTree} cupType={cup.type} />
          </div>
        )}
      </div>
    </div>
  )
}

function getTournamentColor(type) {
  const colorMap = {
    LEAGUE: colors.tournament.league,
    ELIMINATION: colors.tournament.elimination,
    GROUP: colors.tournament.group,
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
}

export default CupDetail
