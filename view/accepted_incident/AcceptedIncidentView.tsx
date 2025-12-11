import React from 'react';
import { TextSegment } from '../shared/components';
import { IncidentStatus, PriorityLevel, Location, Note } from '../shared/types';
import {
  IncidentHeader,
  SystemRecommendationPanel,
  OperatorNotesPanel,
  LocationPanel,
  FeedbackPanel,
  ActionButtonsPanel,
  SidebarNav,
} from './components';

interface RecentReport {
  id: string;
  label: string;
}

interface AcceptedIncidentViewProps {
  reportId: string;
  reportType: string;
  status: IncidentStatus;
  priority: PriorityLevel;
  dateTime: string;
  transcriptionSegments: TextSegment[];
  confidence: number;
  notes: Note[];
  location: Location;
  feedbackValue: 'yes' | 'no' | null;
  isAddingNote: boolean;
  newNoteContent: string;
  recentReports: RecentReport[];
  onEditText: () => void;
  onNewNoteChange: (value: string) => void;
  onAddNoteClick: () => void;
  onSaveNote: () => void;
  onCancelNote: () => void;
  onOpenMap: () => void;
  onFeedbackChange: (value: 'yes' | 'no') => void;
  onTransfer: () => void;
  onClose: () => void;
  onReportClick: (id: string) => void;
  onNavigateToDashboard: () => void;
}

export const AcceptedIncidentView: React.FC<AcceptedIncidentViewProps> = ({
  reportId,
  reportType,
  status,
  priority,
  dateTime,
  transcriptionSegments,
  confidence,
  notes,
  location,
  feedbackValue,
  isAddingNote,
  newNoteContent,
  recentReports,
  onEditText,
  onNewNoteChange,
  onAddNoteClick,
  onSaveNote,
  onCancelNote,
  onOpenMap,
  onFeedbackChange,
  onTransfer,
  onClose,
  onReportClick,
  onNavigateToDashboard,
}) => {
  return (
    <div className="min-h-screen bg-gray-100 [direction:rtl]">
      <div className="flex">
        <div className="hidden lg:block w-64 p-4 border-l border-gray-200 bg-white min-h-screen">
          <SidebarNav
            recentReports={recentReports}
            onReportClick={onReportClick}
            onNavigateToDashboard={onNavigateToDashboard}
          />
        </div>

        <div className="flex-1 flex flex-col">
          <main className="flex-1 p-4 sm:p-6 space-y-4">
            <IncidentHeader
              reportId={reportId}
              reportType={reportType}
              status={status}
              priority={priority}
              dateTime={dateTime}
            />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2 space-y-4">
                <SystemRecommendationPanel
                  segments={transcriptionSegments}
                  confidence={confidence}
                  onEditText={onEditText}
                />

                <OperatorNotesPanel
                  notes={notes}
                  isAddingNote={isAddingNote}
                  newNoteContent={newNoteContent}
                  onNewNoteChange={onNewNoteChange}
                  onAddNoteClick={onAddNoteClick}
                  onSaveNote={onSaveNote}
                  onCancelNote={onCancelNote}
                />
              </div>

              <div className="space-y-4">
                <LocationPanel location={location} onOpenMap={onOpenMap} />

                <FeedbackPanel
                  value={feedbackValue}
                  onChange={onFeedbackChange}
                />
              </div>
            </div>
          </main>

          <ActionButtonsPanel onTransfer={onTransfer} onClose={onClose} />
        </div>
      </div>
    </div>
  );
};

export default AcceptedIncidentView;
