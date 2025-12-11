export type SeverityLevel = 'high' | 'medium' | 'low' | 'critical';

export type PriorityLevel = 'urgent' | 'high' | 'medium' | 'low';

export type IncidentStatus = 'new' | 'pending' | 'in_progress' | 'resolved' | 'closed';

export type IncidentType = 'traffic_accident' | 'fire' | 'medical' | 'security' | 'other';

export type AuthorityType = 'traffic' | 'civil_defense' | 'ambulance' | 'police' | 'municipality';

export interface Incident {
  id: string;
  type: IncidentType;
  status: IncidentStatus;
  severity: SeverityLevel;
  priority: PriorityLevel;
  description: string;
  location: Location;
  callerInfo: CallerInfo;
  responsibleAuthority: AuthorityType;
  createdAt: string;
  updatedAt: string;
  notes: Note[];
  tags: string[];
  confidence?: number;
  transcription?: string;
  audioUrl?: string;
}

export interface Location {
  address: string;
  latitude?: number;
  longitude?: number;
  mapUrl?: string;
}

export interface CallerInfo {
  name: string;
  phone: string;
}

export interface Note {
  id: string;
  content: string;
  createdAt: string;
  createdBy?: string;
}

export interface StatusLogEntry {
  id: string;
  message: string;
  timestamp: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export interface FilterOptions {
  severity?: SeverityLevel;
  status?: IncidentStatus;
  type?: IncidentType;
  authority?: AuthorityType;
  dateFrom?: string;
  dateTo?: string;
  searchQuery?: string;
}

export interface QuickFilter {
  id: string;
  label: string;
  value: string;
}

export interface SelectOption {
  value: string;
  label: string;
}

export interface AudioPlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
}

export interface CallSession {
  id: string;
  startTime: string;
  duration: number;
  isLive: boolean;
  callerInfo: CallerInfo;
  transcription: string;
  analysis?: IncidentAnalysis;
}

export interface IncidentAnalysis {
  type: IncidentType;
  severity: SeverityLevel;
  confidence: number;
  suggestedAuthority: AuthorityType;
  extractedKeywords: string[];
}

export interface ActionHandler {
  onConfirm?: () => void;
  onTransfer?: () => void;
  onClose?: () => void;
  onRequestInfo?: () => void;
  onSave?: () => void;
  onCancel?: () => void;
  onEndCall?: () => void;
}

export interface NavigationHandler {
  onNavigateToIncident?: (id: string) => void;
  onNavigateToList?: () => void;
  onNavigateToRealtime?: () => void;
  onNavigateToDashboard?: () => void;
}
