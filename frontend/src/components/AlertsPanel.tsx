import { useState } from 'react'
import { AlertTriangle, MapPin, Check, Search, Filter } from 'lucide-react'
import { Alert } from '../types'

interface AlertsPanelProps {
  alerts: Alert[];
  onAcknowledge: (id: number) => void;
}

export function AlertsPanel({ alerts, onAcknowledge }: AlertsPanelProps) {
  const [filter, setFilter] = useState<string>('all') // all, critical, high, medium, low
  const [search, setSearch] = useState('')

  const filteredAlerts = alerts.filter(a => {
    const matchesFilter = filter === 'all' || a.severity === filter
    const matchesSearch = a.message.toLowerCase().includes(search.toLowerCase()) || 
                          a.alert_type.toLowerCase().includes(search.toLowerCase())
    return matchesFilter && matchesSearch
  })

  return (
    <div className="panel-container">
      <div className="panel-header">
        <div className="panel-title">
          <h2>Alert Management</h2>
          <span className="badge badge-neutral">{alerts.length} Total</span>
        </div>
        <div className="panel-actions">
          <div className="search-box">
            <Search size={18} />
            <input 
              type="text" 
              placeholder="Search alerts..." 
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <div className="filter-tabs">
            {['all', 'critical', 'high'].map(f => (
              <button 
                key={f}
                className={`filter-tab ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="alerts-grid">
        {filteredAlerts.map(alert => (
          <div key={alert.id} className={`alert-card ${alert.severity}`}>
            <div className="alert-card-header">
              <div className="alert-badge">
                <AlertTriangle size={16} />
                {alert.severity}
              </div>
              <span className="alert-timestamp">
                {new Date(alert.created_at).toLocaleTimeString()}
              </span>
            </div>
            
            <div className="alert-card-body">
              <h4>{alert.alert_type}</h4>
              <p>{alert.message}</p>
              {alert.location && (
                <div className="location-tag">
                  <MapPin size={14} /> {alert.location}
                </div>
              )}
            </div>

            <div className="alert-card-footer">
              {alert.status === 'active' ? (
                <button 
                  className="btn btn-sm btn-acknowledge"
                  onClick={() => onAcknowledge(alert.id)}
                >
                  <Check size={16} /> Acknowledge
                </button>
              ) : (
                <span className="status-label resolved">
                  <Check size={14} /> Acknowledged
                </span>
              )}
            </div>
          </div>
        ))}
        {filteredAlerts.length === 0 && (
          <div className="empty-state-large">
            <div className="empty-icon"><Filter size={48} /></div>
            <h3>No alerts found</h3>
            <p>Try adjusting your search or filters</p>
          </div>
        )}
      </div>
    </div>
  )
}
