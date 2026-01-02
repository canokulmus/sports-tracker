// src/components/Game/ScorersList.jsx

function ScorersList({ scorers = [] }) {
  if (!scorers?.length) return null

  return (
    <div className="scorers-list">
      {scorers.map((scorer, idx) => (
        <span key={idx} className="scorer-item">
          ⚽ {scorer?.player ?? 'Bilinmeyen'} {scorer?.minute ? `${scorer.minute}'` : ''}
        </span>
      ))}
    </div>
  )
}

export default ScorersList