import React from 'react';
import { TextSegment } from '../shared/components';
import { SeverityLevel, StatusLogEntry, SelectOption } from '../shared/types';
import {
  CallHeader,
  TranscriptionPanel,
  AnalysisPanel,
  QuickTagsPanel,
  QuickNotesPanel,
  SuggestedActionsPanel,
  StatusLogPanel,
  VoiceControlPanel,
  CallFooter,
} from './components';

interface QuickTag {
  id: string;
  label: string;
  variant: 'urgent' | 'accident' | 'injury' | 'fire' | 'custom';
}

interface TranscriptionData {
  original_text: string;
  original_language: string;
  translated_text: string | null;
  translated_language: string | null;
  translation_enabled: boolean;
}

interface RealtimeIncidentViewProps {
  callDuration: number;
  isLive: boolean;
  isSaving: boolean;
  isAutoSaving: boolean;
  transcriptionSegments: TextSegment[];
  /** New: Transcription data with both original and translated text */
  transcriptionData?: TranscriptionData | null;
  reportType: string;
  severity: SeverityLevel | '';
  responsibleAuthority: string;
  confidence: number;
  reportTypeOptions: SelectOption[];
  authorityOptions: SelectOption[];
  quickTags: QuickTag[];
  selectedTags: string[];
  quickNotes: string;
  statusLogEntries: StatusLogEntry[];
  volume: number;
  isTranslationEnabled: boolean;
  onSave: () => void;
  onEndCall: () => void;
  onEditText: () => void;
  onReportTypeChange: (value: string) => void;
  onSeverityChange: (value: SeverityLevel) => void;
  onAuthorityChange: (value: string) => void;
  onTagToggle: (tagId: string) => void;
  onQuickNotesChange: (value: string) => void;
  onSuggestedAction: (actionId: string) => void;
  onVolumeChange: (value: number) => void;
  onTranslationToggle: (enabled: boolean) => void;
  onConfirm: () => void;
}

export const RealtimeIncidentView: React.FC<RealtimeIncidentViewProps> = ({
  callDuration,
  isLive,
  isSaving,
  isAutoSaving,
  transcriptionSegments,
  transcriptionData,
  reportType,
  severity,
  responsibleAuthority,
  confidence,
  reportTypeOptions,
  authorityOptions,
  quickTags,
  selectedTags,
  quickNotes,
  statusLogEntries,
  volume,
  isTranslationEnabled,
  onSave,
  onEndCall,
  onEditText,
  onReportTypeChange,
  onSeverityChange,
  onAuthorityChange,
  onTagToggle,
  onQuickNotesChange,
  onSuggestedAction,
  onVolumeChange,
  onTranslationToggle,
  onConfirm,
}) => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col [direction:rtl]">
      <CallHeader
        callDuration={callDuration}
        isLive={isLive}
        onSave={onSave}
        onEndCall={onEndCall}
        isSaving={isSaving}
      />

      <main className="flex-1 p-4 sm:p-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
          <div className="lg:col-span-5 space-y-4">
            <TranscriptionPanel
              segments={transcriptionSegments}
              transcriptionData={transcriptionData}
              isTranslationEnabled={isTranslationEnabled}
              onEditText={onEditText}
            />
          </div>

          <div className="lg:col-span-4 space-y-4">
            <AnalysisPanel
              reportType={reportType}
              severity={severity}
              responsibleAuthority={responsibleAuthority}
              confidence={confidence}
              reportTypeOptions={reportTypeOptions}
              authorityOptions={authorityOptions}
              onReportTypeChange={onReportTypeChange}
              onSeverityChange={onSeverityChange}
              onAuthorityChange={onAuthorityChange}
            />

            <QuickTagsPanel
              tags={quickTags}
              selectedTags={selectedTags}
              onTagToggle={onTagToggle}
            />

            <QuickNotesPanel
              notes={quickNotes}
              onNotesChange={onQuickNotesChange}
            />
          </div>

          <div className="lg:col-span-3 space-y-4">
            <SuggestedActionsPanel onAction={onSuggestedAction} />

            <StatusLogPanel entries={statusLogEntries} />

            <VoiceControlPanel
              volume={volume}
              isTranslationEnabled={isTranslationEnabled}
              onVolumeChange={onVolumeChange}
              onTranslationToggle={onTranslationToggle}
            />
          </div>
        </div>
      </main>

      <CallFooter onConfirm={onConfirm} isAutoSaving={isAutoSaving} />
    </div>
  );
};

export default RealtimeIncidentView;
