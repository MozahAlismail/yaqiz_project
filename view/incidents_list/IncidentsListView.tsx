import React from 'react';
import { QuickFilter, SelectOption, AudioPlayerState, SeverityLevel, IncidentStatus, AuthorityType } from '../shared/types';
import { texts } from '../i18n/texts';
import {
  FilterPanel,
  IncidentList,
  IncidentDetailsPanel,
  SearchHeader,
} from './components';

interface IncidentItem {
  id: string;
  description: string;
  status: IncidentStatus;
  severity: SeverityLevel;
  authority: AuthorityType;
  dateTime: string;
}

interface SelectedIncidentDetails {
  id: string;
  dateTime: string;
  status: IncidentStatus;
  isPriority: boolean;
  transcription: string;
  analysis: string;
}

interface IncidentsListViewProps {
  searchQuery: string;
  showFilters: boolean;
  quickFilters: QuickFilter[];
  selectedQuickFilter: string;
  severityOptions: SelectOption[];
  selectedSeverity: string;
  incidentTypeOptions: SelectOption[];
  selectedIncidentType: string;
  authorityOptions: SelectOption[];
  selectedAuthority: string;
  monthOptions: SelectOption[];
  selectedMonth: string;
  yearOptions: SelectOption[];
  selectedYear: string;
  statusOptions: SelectOption[];
  incidents: IncidentItem[];
  selectedIncidentIds: string[];
  selectedIncident: SelectedIncidentDetails | null;
  audioState: AudioPlayerState;
  onSearchChange: (value: string) => void;
  onFilterToggle: () => void;
  onQuickFilterChange: (id: string) => void;
  onSeverityChange: (value: string) => void;
  onIncidentTypeChange: (value: string) => void;
  onAuthorityChange: (value: string) => void;
  onMonthChange: (value: string) => void;
  onYearChange: (value: string) => void;
  onApplyFilters: () => void;
  onCancelFilters: () => void;
  onSelectAll: (selected: boolean) => void;
  onSelectItem: (id: string, selected: boolean) => void;
  onViewItem: (id: string) => void;
  onStatusChange: (value: string) => void;
  onPriorityToggle: (enabled: boolean) => void;
  onAudioPlayPause: () => void;
  onAudioSeek: (time: number) => void;
  onAudioVolumeChange: (volume: number) => void;
  onAudioMuteToggle: () => void;
  onRequestInfo: () => void;
  onConfirm: () => void;
}

export const IncidentsListView: React.FC<IncidentsListViewProps> = ({
  searchQuery,
  showFilters,
  quickFilters,
  selectedQuickFilter,
  severityOptions,
  selectedSeverity,
  incidentTypeOptions,
  selectedIncidentType,
  authorityOptions,
  selectedAuthority,
  monthOptions,
  selectedMonth,
  yearOptions,
  selectedYear,
  statusOptions,
  incidents,
  selectedIncidentIds,
  selectedIncident,
  audioState,
  onSearchChange,
  onFilterToggle,
  onQuickFilterChange,
  onSeverityChange,
  onIncidentTypeChange,
  onAuthorityChange,
  onMonthChange,
  onYearChange,
  onApplyFilters,
  onCancelFilters,
  onSelectAll,
  onSelectItem,
  onViewItem,
  onStatusChange,
  onPriorityToggle,
  onAudioPlayPause,
  onAudioSeek,
  onAudioVolumeChange,
  onAudioMuteToggle,
  onRequestInfo,
  onConfirm,
}) => {
  return (
    <div className="min-h-screen bg-gray-100 [direction:rtl]">
      <div className="flex">
        {showFilters && (
          <aside className="w-80 p-4 border-l border-gray-200 bg-white min-h-screen hidden lg:block">
            <FilterPanel
              quickFilters={quickFilters}
              selectedQuickFilter={selectedQuickFilter}
              severityOptions={severityOptions}
              selectedSeverity={selectedSeverity}
              incidentTypeOptions={incidentTypeOptions}
              selectedIncidentType={selectedIncidentType}
              authorityOptions={authorityOptions}
              selectedAuthority={selectedAuthority}
              monthOptions={monthOptions}
              selectedMonth={selectedMonth}
              yearOptions={yearOptions}
              selectedYear={selectedYear}
              onQuickFilterChange={onQuickFilterChange}
              onSeverityChange={onSeverityChange}
              onIncidentTypeChange={onIncidentTypeChange}
              onAuthorityChange={onAuthorityChange}
              onMonthChange={onMonthChange}
              onYearChange={onYearChange}
              onApply={onApplyFilters}
              onCancel={onCancelFilters}
            />
          </aside>
        )}

        <main className="flex-1 p-4 sm:p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <SearchHeader
                searchQuery={searchQuery}
                onSearchChange={onSearchChange}
                onFilterToggle={onFilterToggle}
                showFilterButton={!showFilters}
              />

              <IncidentList
                incidents={incidents}
                selectedIds={selectedIncidentIds}
                onSelectAll={onSelectAll}
                onSelectItem={onSelectItem}
                onViewItem={onViewItem}
              />
            </div>

            <div>
              {selectedIncident ? (
                <IncidentDetailsPanel
                  incidentId={selectedIncident.id}
                  dateTime={selectedIncident.dateTime}
                  status={selectedIncident.status}
                  isPriority={selectedIncident.isPriority}
                  transcription={selectedIncident.transcription}
                  analysis={selectedIncident.analysis}
                  statusOptions={statusOptions}
                  audioState={audioState}
                  onStatusChange={onStatusChange}
                  onPriorityToggle={onPriorityToggle}
                  onAudioPlayPause={onAudioPlayPause}
                  onAudioSeek={onAudioSeek}
                  onAudioVolumeChange={onAudioVolumeChange}
                  onAudioMuteToggle={onAudioMuteToggle}
                  onRequestInfo={onRequestInfo}
                  onConfirm={onConfirm}
                />
              ) : (
                <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
                  <p className="text-gray-500">
                    {texts.common.noData}
                  </p>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default IncidentsListView;
