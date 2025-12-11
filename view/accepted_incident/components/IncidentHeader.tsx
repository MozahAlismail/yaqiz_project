import React from 'react';
import { Badge } from '../../shared/components';
import { IncidentStatus, PriorityLevel } from '../../shared/types';
import { IconClock } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface IncidentHeaderProps {
  reportId: string;
  reportType: string;
  status: IncidentStatus;
  priority: PriorityLevel;
  dateTime: string;
}

const statusVariants: Record<IncidentStatus, 'default' | 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
  new: 'info',
  pending: 'warning',
  in_progress: 'default',
  resolved: 'success',
  closed: 'neutral',
};

const priorityVariants: Record<PriorityLevel, 'default' | 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
  urgent: 'danger',
  high: 'warning',
  medium: 'info',
  low: 'success',
};

const statusLabels: Record<IncidentStatus, string> = {
  new: texts.incident.newReport,
  pending: texts.incident.pendingReview,
  in_progress: texts.incident.inProgress,
  resolved: texts.incident.resolved,
  closed: texts.incident.closed,
};

const priorityLabels: Record<PriorityLevel, string> = {
  urgent: texts.priorities.urgent,
  high: texts.priorities.high,
  medium: texts.priorities.medium,
  low: texts.priorities.low,
};

export const IncidentHeader: React.FC<IncidentHeaderProps> = ({
  reportId,
  reportType,
  status,
  priority,
  dateTime,
}) => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div>
            <span className="text-xs text-gray-500">{texts.incident.reportId}</span>
            <p className="text-lg font-bold text-gray-900">#{reportId}</p>
          </div>
          <div className="h-8 w-px bg-gray-200" />
          <div>
            <span className="text-xs text-gray-500">{texts.incident.reportType}</span>
            <p className="text-sm font-medium text-gray-900">{reportType}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant={statusVariants[status]} size="md">
            {statusLabels[status]}
          </Badge>
          <Badge variant={priorityVariants[priority]} size="md">
            {priorityLabels[priority]}
          </Badge>
          <div className="flex items-center gap-1.5 text-gray-500">
            <IconClock size={16} />
            <span className="text-sm">{dateTime}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentHeader;
