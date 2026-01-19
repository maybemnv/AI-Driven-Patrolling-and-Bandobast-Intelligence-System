import { useState, useEffect } from 'react'
import { FileText, Sparkles, Calendar } from 'lucide-react'
import { API_BASE } from '../config'
import { Summary } from '../types'

export function SummariesPanel() {
  const [loading, setLoading] = useState(false)
  const [summaries, setSummaries] = useState<Summary[]>([])
  const [selectedSummary, setSelectedSummary] = useState<Summary | null>(null)

  useEffect(() => {
    fetchSummaries()
  }, [])

  const fetchSummaries = async () => {
    try {
      const res = await fetch(`${API_BASE}/summaries?limit=20`)
      const data = await res.json()
      // Handle { items: [...] } or [...]
      const items = data.items ? data.items : (Array.isArray(data) ? data : [])
      setSummaries(items)
      // Auto-select first if available
      if (items.length > 0 && !selectedSummary) {
        setSelectedSummary(items[0])
      }
    } catch (e) {
      console.error('Fetch summaries error:', e)
    }
  }

  const generateBrief = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/summaries/generate/daily`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      })
      const data = await res.json()
      setSelectedSummary(data)
      fetchSummaries() // Refresh list
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  return (
    <div className="panel-container">
      <div className="summary-layout">
        {/* Sidebar List */}
        <div className="summary-list-panel">
          <div className="panel-header">
            <h3>History</h3>
            <button 
              className="btn btn-primary btn-sm btn-icon-text" 
              onClick={generateBrief} 
              disabled={loading}
            >
              {loading ? <span className="spinner-sm"></span> : <Sparkles size={16} />}
              <span>New Daily Brief</span>
            </button>
          </div>
          <div className="summary-scroller">
            {summaries.map(s => (
              <div 
                key={s.id} 
                className={`summary-item ${selectedSummary?.id === s.id ? 'active' : ''}`}
                onClick={() => setSelectedSummary(s)}
              >
                <div className="summary-icon">
                  <FileText size={18} />
                </div>
                <div className="summary-meta">
                  <span className="summary-type">{s.summary_type}</span>
                  <span className="summary-date">
                    {new Date(s.created_at).toLocaleString(undefined, {
                      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                    })}
                  </span>
                </div>
              </div>
            ))}
             {summaries.length === 0 && <div className="empty-state-text">No summaries yet</div>}
          </div>
        </div>

        {/* Content View */}
        <div className="summary-content-panel">
          {selectedSummary ? (
            <div className="summary-viewer">
              <div className="viewer-header">
                <div>
                  <h2>{selectedSummary.summary_type}</h2>
                  <div className="viewer-meta">
                    <span className="meta-tag"><Calendar size={14} /> {new Date(selectedSummary.created_at).toLocaleString()}</span>
                    {selectedSummary.tokens_used && (
                      <span className="meta-tag token-tag">
                        <Sparkles size={14} /> {selectedSummary.tokens_used} tokens
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="markdown-body">
                {selectedSummary.markdown || selectedSummary.raw_text}
              </div>
            </div>
          ) : (
            <div className="empty-state-large">
              <div className="empty-icon"><FileText size={48} /></div>
              <h3>Select a summary</h3>
              <p>View details of past intelligence briefs</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
