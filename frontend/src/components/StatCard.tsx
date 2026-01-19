import { LucideIcon } from 'lucide-react'

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: number;
  color: 'blue' | 'green' | 'amber' | 'red';
}

export function StatCard({ icon: Icon, label, value, color }: StatCardProps) {
  return (
    <div className={`stat-card ${color}`}>
      <div className="stat-icon-wrapper">
        <Icon size={24} className="stat-icon" />
      </div>
      <div className="stat-content">
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  )
}
