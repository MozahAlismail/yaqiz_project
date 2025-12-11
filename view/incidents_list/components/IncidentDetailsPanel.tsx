import React from 'react';
import { Card, Badge, Select, Toggle, Button, AudioPlayer } from '../../shared/components';
import { SeverityLevel, IncidentStatus, AudioPlayerState, SelectOption } from '../../shared/types';
import { IconInfo } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface IncidentDetailsPanelProps {
  incidentId: string;
  dateTime: string;
  status: IncidentStatus;
  isPriority: boolean;
  transcription: string;
  analysis: string;
  statusOptions: SelectOption[];
  audioState: AudioPlayerState;
  onStatusChange: (value: string) => void;
  onPriorityToggle: (enabled: boolean) => void;
  onAudioPlayPause: () => void;
  onAudioSeek: (time: number) => void;
  onAudioVolumeChange: (volume: number) => void;
  onAudioMuteToggle: () => void;
  onRequestInfo: () => void;
  onConfirm: () => void;
}

const statusLabels: Record<IncidentStatus, string> = {
  new: texts.incident.newReport,
  pending: texts.incident.pendingReview,
  in_progress: texts.incident.inProgress,
  resolved: texts.incident.resolved,
  closed: texts.incident.closed,
};

export const IncidentDetailsPanel: React.FC<IncidentDetailsPanelProps> = ({
  incidentId,
  dateTime,
  status,
  isPriority,
  transcription,
  analysis,
  statusOptions,
  audioState,
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
    <Card className="h-full">
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <span className="text-xs text-gray-500">{texts.incident.reportId}</span>
            <p className="text-lg font-bold text-gray-900">#{incidentId}</p>
          </div>
          <Select
            value={status}
            onChange={onStatusChange}
            options={statusOptions}
            className="w-40"
          />
        </div>

        <div className="flex items-center justify-between py-3 border-y border-gray-100">
          <div>
            <span className="text-xs text-gray-500">{texts.incident.dateTime}</span>
            <p className="text-sm text-gray-700">{dateTime}</p>
          </div>
          <Toggle
            checked={isPriority}
            onChange={onPriorityToggle}
            label={texts.incident.priority}
          />
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">
            {texts.incidentsList.audioPlayer}
          </h4>
          <AudioPlayer
            state={audioState}
            onPlayPause={onAudioPlayPause}
            onSeek={onAudioSeek}
            onVolumeChange={onAudioVolumeChange}
            onMuteToggle={onAudioMuteToggle}
          />
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            {texts.incidentsList.transcription}
          </h4>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-700 leading-relaxed [direction:rtl]">
              {transcription}
            </p>
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <IconInfo size={16} className="text-[#0b5ac1]" />
            <h4 className="text-sm font-medium text-gray-700">
              {texts.incidentsList.analysis}
            </h4>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
            <p className="text-sm text-gray-700 leading-relaxed [direction:rtl]">
              {analysis}
            </p>
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <Button variant="ghost" fullWidth onClick={onRequestInfo}>
            {texts.actions.requestMoreInfo}
          </Button>
          <Button variant="success" fullWidth onClick={onConfirm}>
            {texts.common.confirm}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default IncidentDetailsPanel;
