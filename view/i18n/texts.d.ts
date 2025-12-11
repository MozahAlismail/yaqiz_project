export interface Texts {
  common: {
    save: string;
    cancel: string;
    confirm: string;
    close: string;
    edit: string;
    delete: string;
    add: string;
    search: string;
    filter: string;
    apply: string;
    yes: string;
    no: string;
    loading: string;
    noData: string;
    viewDetails: string;
    back: string;
    next: string;
    previous: string;
    all: string;
    autoSaving: string;
    live: string;
  };
  navigation: {
    alertsSystem: string;
    dashboard: string;
    incidents: string;
    reports: string;
    settings: string;
    recentReports: string;
  };
  incident: {
    reportId: string;
    reportType: string;
    status: string;
    priority: string;
    severity: string;
    dateTime: string;
    location: string;
    description: string;
    callerInfo: string;
    callerName: string;
    callerPhone: string;
    responsibleAuthority: string;
    incidentType: string;
    newReport: string;
    pendingReview: string;
    inProgress: string;
    resolved: string;
    closed: string;
    trafficAccident: string;
    fire: string;
    medical: string;
    security: string;
    other: string;
  };
  severity: {
    high: string;
    medium: string;
    low: string;
    critical: string;
    nonUrgent: string;
  };
  priorities: {
    urgent: string;
    high: string;
    medium: string;
    low: string;
  };
  authorities: {
    traffic: string;
    civilDefense: string;
    ambulance: string;
    police: string;
    municipality: string;
  };
  actions: {
    transfer: string;
    closeReport: string;
    endCall: string;
    confirmReport: string;
    transferToAuthority: string;
    requestMoreInfo: string;
    addNote: string;
    saveNote: string;
    viewOnMap: string;
  };
  realtime: {
    systemAnalysis: string;
    convertedText: string;
    quickTags: string;
    quickNotes: string;
    suggestedActions: string;
    statusLog: string;
    voiceControl: string;
    translation: string;
    callDuration: string;
    reportReceived: string;
    textExtracted: string;
    caseClassified: string;
    awaitingDecision: string;
    confidence: string;
  };
  tags: {
    urgent: string;
    accident: string;
    injury: string;
    fire: string;
    theft: string;
  };
  acceptedIncident: {
    systemRecommendation: string;
    extractedText: string;
    operatorNotes: string;
    locationDetails: string;
    feedbackQuestion: string;
    analysisAccuracy: string;
    confidenceLevel: string;
    editText: string;
  };
  incidentsList: {
    filterReports: string;
    quickFilters: string;
    severityFilter: string;
    incidentTypeFilter: string;
    authorityFilter: string;
    dateFilter: string;
    monthFilter: string;
    yearFilter: string;
    transcription: string;
    analysis: string;
    audioPlayer: string;
    selectAll: string;
  };
  months: {
    january: string;
    february: string;
    march: string;
    april: string;
    may: string;
    june: string;
    july: string;
    august: string;
    september: string;
    october: string;
    november: string;
    december: string;
  };
  placeholders: {
    searchIncidents: string;
    enterNotes: string;
    selectOption: string;
    selectAuthority: string;
    selectIncidentType: string;
    selectMonth: string;
    selectYear: string;
  };
  validation: {
    required: string;
    invalidPhone: string;
    invalidEmail: string;
  };
  notifications: {
    saveSuccess: string;
    saveError: string;
    confirmSuccess: string;
    transferSuccess: string;
    deleteConfirm: string;
  };
  sampleData: {
    address: string;
    sampleDescription: string;
    callerStatement: string;
  };
}

export const texts: Texts;
export default texts;
