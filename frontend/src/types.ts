export interface Alert {
  id: number;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  location?: string;
  status: 'active' | 'resolved' | 'acknowledged';
  created_at: string;
}

export interface Patrol {
  id: number;
  officer_id: string;
  officer_name: string;
  zone: string;
  started_at: string;
  status: string;
}

export interface Summary {
  id: number;
  summary_type: string;
  markdown?: string;
  raw_text?: string;
  tokens_used?: number;
  created_at: string;
}

export interface Stats {
  alerts: number;
  patrols: number;
  active: number;
  resolved: number;
}
