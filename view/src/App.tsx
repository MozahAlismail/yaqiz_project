import React, { useState, useCallback } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Layout } from './components/Layout';
import { LanguageProvider } from './context/LanguageContext';
import { ThemeProvider } from './context/ThemeContext';

// Import views
import { RealtimeIncidentView } from '../realtime_incident';
import { AcceptedIncidentView } from '../accepted_incident';
import { IncidentsListView } from '../incidents_list';

// Import types
import type {
  SeverityLevel,
  IncidentStatus,
  AuthorityType,
  StatusLogEntry,
  SelectOption,
  QuickFilter,
  AudioPlayerState,
  Note,
  Location,
} from '../shared/types';
import type { TextSegment } from '../shared/components';

type ViewType = 'realtime' | 'accepted' | 'incidents-list';

// Mock data for testing without backend
const mockQuickTags = [
  { id: '1', label: '#عاجل', variant: 'urgent' as const },
  { id: '2', label: '#حادث', variant: 'accident' as const },
  { id: '3', label: '#إصابة', variant: 'injury' as const },
  { id: '4', label: '#حريق', variant: 'fire' as const },
];

const mockStatusLogEntries: StatusLogEntry[] = [
  { id: '1', message: 'تم إستقبال البلاغ', timestamp: new Date().toISOString(), type: 'info' },
  { id: '2', message: 'تم استخراج النص', timestamp: new Date().toISOString(), type: 'success' },
  { id: '3', message: 'تم تصنيف الحالة', timestamp: new Date().toISOString(), type: 'success' },
  { id: '4', message: 'في انتظار قرار المشغل', timestamp: new Date().toISOString(), type: 'warning' },
];

const mockTranscriptionSegments: TextSegment[] = [
  { text: 'أنا أتصل من طريق الملك فهد، هناك حادث سيارتين. ', type: 'normal' },
  { text: 'اسمي محمد', type: 'name' },
  { text: ' وأرى سيارتين متضررتين على الطريق.', type: 'normal' },
];

const mockReportTypeOptions: SelectOption[] = [
  { value: 'traffic_accident', label: 'حادث مروري' },
  { value: 'fire', label: 'حريق' },
  { value: 'medical', label: 'طبي' },
  { value: 'security', label: 'أمني' },
  { value: 'other', label: 'أخرى' },
];

const mockAuthorityOptions: SelectOption[] = [
  { value: 'traffic', label: 'المرور' },
  { value: 'civil_defense', label: 'الدفاع المدني' },
  { value: 'ambulance', label: 'الإسعاف' },
  { value: 'police', label: 'الشرطة' },
  { value: 'municipality', label: 'البلدية' },
];

const mockQuickFilters: QuickFilter[] = [
  { id: 'all', label: 'الكل', value: 'all' },
  { id: 'urgent', label: 'عاجل', value: 'urgent' },
  { id: 'high', label: 'مرتفعة', value: 'high' },
  { id: 'pending', label: 'قيد المراجعة', value: 'pending' },
];

const mockSeverityOptions: SelectOption[] = [
  { value: 'critical', label: 'حرج' },
  { value: 'high', label: 'عالي' },
  { value: 'medium', label: 'متوسط' },
  { value: 'low', label: 'منخفض' },
];

const mockIncidentTypeOptions: SelectOption[] = [
  { value: 'traffic_accident', label: 'حادث مروري' },
  { value: 'fire', label: 'حريق' },
  { value: 'medical', label: 'طبي' },
  { value: 'security', label: 'أمني' },
  { value: 'other', label: 'أخرى' },
];

const mockMonthOptions: SelectOption[] = [
  { value: '1', label: 'يناير' },
  { value: '2', label: 'فبراير' },
  { value: '3', label: 'مارس' },
  { value: '4', label: 'أبريل' },
  { value: '5', label: 'مايو' },
  { value: '6', label: 'يونيو' },
  { value: '7', label: 'يوليو' },
  { value: '8', label: 'أغسطس' },
  { value: '9', label: 'سبتمبر' },
  { value: '10', label: 'أكتوبر' },
  { value: '11', label: 'نوفمبر' },
  { value: '12', label: 'ديسمبر' },
];

const mockYearOptions: SelectOption[] = [
  { value: '2024', label: '2024' },
  { value: '2025', label: '2025' },
];

const mockStatusOptions: SelectOption[] = [
  { value: 'new', label: 'جديد' },
  { value: 'pending', label: 'قيد المراجعة' },
  { value: 'in_progress', label: 'قيد التنفيذ' },
  { value: 'resolved', label: 'تم الحل' },
  { value: 'closed', label: 'مغلق' },
];

const mockIncidents = [
  {
    id: '1',
    description: 'حادث سير على طريق الملك فهد',
    status: 'pending' as IncidentStatus,
    severity: 'high' as SeverityLevel,
    authority: 'traffic' as AuthorityType,
    dateTime: new Date().toISOString(),
  },
  {
    id: '2',
    description: 'حريق في مبنى سكني',
    status: 'in_progress' as IncidentStatus,
    severity: 'critical' as SeverityLevel,
    authority: 'civil_defense' as AuthorityType,
    dateTime: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: '3',
    description: 'حالة طبية طارئة',
    status: 'new' as IncidentStatus,
    severity: 'medium' as SeverityLevel,
    authority: 'ambulance' as AuthorityType,
    dateTime: new Date(Date.now() - 7200000).toISOString(),
  },
];

const mockNotes: Note[] = [
  {
    id: '1',
    content: 'تم التواصل مع الجهات المختصة',
    createdAt: new Date().toISOString(),
    createdBy: 'المشغل أحمد',
  },
  {
    id: '2',
    content: 'تم إرسال فريق الإسعاف',
    createdAt: new Date(Date.now() - 600000).toISOString(),
    createdBy: 'المشغل محمد',
  },
];

const mockLocation: Location = {
  address: 'الرياض، طريق الملك فهد، بالقرب من برج المملكة',
  latitude: 24.7136,
  longitude: 46.6753,
  mapUrl: 'https://maps.google.com/?q=24.7136,46.6753',
};

const mockRecentReports = [
  { id: '1', label: 'بلاغ #12345' },
  { id: '2', label: 'بلاغ #12344' },
  { id: '3', label: 'بلاغ #12343' },
];

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>('incidents-list');

  // Realtime view state
  const [callDuration] = useState(125);
  const [isLive, setIsLive] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isAutoSaving] = useState(true);
  const [reportType, setReportType] = useState('traffic_accident');
  const [severity, setSeverity] = useState<SeverityLevel | ''>('high');
  const [responsibleAuthority, setResponsibleAuthority] = useState('traffic');
  const [selectedTags, setSelectedTags] = useState<string[]>(['1']);
  const [quickNotes, setQuickNotes] = useState('');
  const [volume, setVolume] = useState(80);
  const [isTranslationEnabled, setIsTranslationEnabled] = useState(true);

  // Incidents list view state
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(true);
  const [selectedQuickFilter, setSelectedQuickFilter] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('');
  const [selectedIncidentType, setSelectedIncidentType] = useState('');
  const [selectedAuthority, setSelectedAuthority] = useState('');
  const [selectedMonth, setSelectedMonth] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedIncidentIds, setSelectedIncidentIds] = useState<string[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>('1');
  const [audioState, setAudioState] = useState<AudioPlayerState>({
    isPlaying: false,
    currentTime: 0,
    duration: 180,
    volume: 80,
    isMuted: false,
  });

  // Accepted incident view state
  const [feedbackValue, setFeedbackValue] = useState<'yes' | 'no' | null>(null);
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [newNoteContent, setNewNoteContent] = useState('');

  // Handlers
  const handleNavigate = useCallback((view: ViewType) => {
    setCurrentView(view);
  }, []);

  const handleTagToggle = useCallback((tagId: string) => {
    setSelectedTags((prev) =>
      prev.includes(tagId) ? prev.filter((id) => id !== tagId) : [...prev, tagId]
    );
  }, []);

  const handleSelectAll = useCallback((selected: boolean) => {
    setSelectedIncidentIds(selected ? mockIncidents.map((i) => i.id) : []);
  }, []);

  const handleSelectItem = useCallback((id: string, selected: boolean) => {
    setSelectedIncidentIds((prev) =>
      selected ? [...prev, id] : prev.filter((i) => i !== id)
    );
  }, []);

  const selectedIncident = selectedIncidentId
    ? {
        id: selectedIncidentId,
        dateTime: mockIncidents.find((i) => i.id === selectedIncidentId)?.dateTime || '',
        status: mockIncidents.find((i) => i.id === selectedIncidentId)?.status || 'new' as IncidentStatus,
        isPriority: true,
        transcription: 'أنا أتصل من طريق الملك فهد، هناك حادث سيارتين. اسمي محمد وأرى سيارتين متضررتين على الطريق.',
        analysis: 'تم تصنيف البلاغ كحادث مروري بدرجة خطورة عالية. يُنصح بإرسال فريق المرور.',
      }
    : null;

  const renderView = () => {
    switch (currentView) {
      case 'realtime':
        return (
          <RealtimeIncidentView
            callDuration={callDuration}
            isLive={isLive}
            isSaving={isSaving}
            isAutoSaving={isAutoSaving}
            transcriptionSegments={mockTranscriptionSegments}
            reportType={reportType}
            severity={severity}
            responsibleAuthority={responsibleAuthority}
            confidence={92}
            reportTypeOptions={mockReportTypeOptions}
            authorityOptions={mockAuthorityOptions}
            quickTags={mockQuickTags}
            selectedTags={selectedTags}
            quickNotes={quickNotes}
            statusLogEntries={mockStatusLogEntries}
            volume={volume}
            isTranslationEnabled={isTranslationEnabled}
            onSave={() => setIsSaving(true)}
            onEndCall={() => setIsLive(false)}
            onEditText={() => console.log('Edit text')}
            onReportTypeChange={setReportType}
            onSeverityChange={setSeverity}
            onAuthorityChange={setResponsibleAuthority}
            onTagToggle={handleTagToggle}
            onQuickNotesChange={setQuickNotes}
            onSuggestedAction={(id) => console.log('Action:', id)}
            onVolumeChange={setVolume}
            onTranslationToggle={setIsTranslationEnabled}
            onConfirm={() => handleNavigate('accepted')}
          />
        );

      case 'accepted':
        return (
          <AcceptedIncidentView
            reportId="RPT-12345"
            reportType="حادث مروري"
            status="pending"
            priority="high"
            dateTime={new Date().toISOString()}
            transcriptionSegments={mockTranscriptionSegments}
            confidence={92}
            notes={mockNotes}
            location={mockLocation}
            feedbackValue={feedbackValue}
            isAddingNote={isAddingNote}
            newNoteContent={newNoteContent}
            recentReports={mockRecentReports}
            onEditText={() => console.log('Edit text')}
            onNewNoteChange={setNewNoteContent}
            onAddNoteClick={() => setIsAddingNote(true)}
            onSaveNote={() => {
              setIsAddingNote(false);
              setNewNoteContent('');
            }}
            onCancelNote={() => {
              setIsAddingNote(false);
              setNewNoteContent('');
            }}
            onOpenMap={() => window.open(mockLocation.mapUrl, '_blank')}
            onFeedbackChange={setFeedbackValue}
            onTransfer={() => console.log('Transfer')}
            onClose={() => handleNavigate('incidents-list')}
            onReportClick={(id) => console.log('Report clicked:', id)}
            onNavigateToDashboard={() => console.log('Navigate to dashboard')}
          />
        );

      case 'incidents-list':
      default:
        return (
          <IncidentsListView
            searchQuery={searchQuery}
            showFilters={showFilters}
            quickFilters={mockQuickFilters}
            selectedQuickFilter={selectedQuickFilter}
            severityOptions={mockSeverityOptions}
            selectedSeverity={selectedSeverity}
            incidentTypeOptions={mockIncidentTypeOptions}
            selectedIncidentType={selectedIncidentType}
            authorityOptions={mockAuthorityOptions}
            selectedAuthority={selectedAuthority}
            monthOptions={mockMonthOptions}
            selectedMonth={selectedMonth}
            yearOptions={mockYearOptions}
            selectedYear={selectedYear}
            statusOptions={mockStatusOptions}
            incidents={mockIncidents}
            selectedIncidentIds={selectedIncidentIds}
            selectedIncident={selectedIncident}
            audioState={audioState}
            onSearchChange={setSearchQuery}
            onFilterToggle={() => setShowFilters((prev) => !prev)}
            onQuickFilterChange={setSelectedQuickFilter}
            onSeverityChange={setSelectedSeverity}
            onIncidentTypeChange={setSelectedIncidentType}
            onAuthorityChange={setSelectedAuthority}
            onMonthChange={setSelectedMonth}
            onYearChange={setSelectedYear}
            onApplyFilters={() => console.log('Apply filters')}
            onCancelFilters={() => console.log('Cancel filters')}
            onSelectAll={handleSelectAll}
            onSelectItem={handleSelectItem}
            onViewItem={setSelectedIncidentId}
            onStatusChange={(value) => console.log('Status change:', value)}
            onPriorityToggle={(enabled) => console.log('Priority toggle:', enabled)}
            onAudioPlayPause={() =>
              setAudioState((prev) => ({ ...prev, isPlaying: !prev.isPlaying }))
            }
            onAudioSeek={(time) => setAudioState((prev) => ({ ...prev, currentTime: time }))}
            onAudioVolumeChange={(vol) => setAudioState((prev) => ({ ...prev, volume: vol }))}
            onAudioMuteToggle={() =>
              setAudioState((prev) => ({ ...prev, isMuted: !prev.isMuted }))
            }
            onRequestInfo={() => console.log('Request info')}
            onConfirm={() => handleNavigate('accepted')}
          />
        );
    }
  };

  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LanguageProvider>
          <Layout currentView={currentView} onNavigate={handleNavigate}>
            {renderView()}
          </Layout>
        </LanguageProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default App;
