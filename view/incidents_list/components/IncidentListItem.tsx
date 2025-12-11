import React from 'react';
import { Badge, Checkbox } from '../../shared/components';
import { SeverityLevel, IncidentStatus, AuthorityType } from '../../shared/types';
import { IconEye } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface IncidentListItemProps {
  id: string;
  description: string;
  status: IncidentStatus;
  severity: SeverityLevel;
  authority: AuthorityType;
  dateTime: string;
  isSelected: boolean;
  onSelect: (selected: boolean) => void;
  onView: () => void;
}

const statusVariants: Record<IncidentStatus, 'default' | 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
  new: 'info',
  pending: 'warning',
  in_progress: 'default',
  resolved: 'success',
  closed: 'neutral',
};

const severityVariants: Record<SeverityLevel, 'default' | 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
  critical: 'danger',
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

const severityLabels: Record<SeverityLevel, string> = {
  critical: texts.severity.critical,
  high: texts.severity.high,
  medium: texts.severity.medium,
  low: texts.severity.low,
};

const authorityLabels: Record<AuthorityType, string> = {
  traffic: texts.authorities.traffic,
  civil_defense: texts.authorities.civilDefense,
  ambulance: texts.authorities.ambulance,
  police: texts.authorities.police,
  municipality: texts.authorities.municipality,
};

export const IncidentListItem: React.FC<IncidentListItemProps> = ({
  id,
  description,
  status,
  severity,
  authority,
  dateTime,
  isSelected,
  onSelect,
  onView,
}) => {
  return (
    <article
      className={`
        bg-white rounded-lg border p-4 transition-colors
        ${isSelected ? 'border-[#0b5ac1] bg-blue-50' : 'border-gray-200 hover:border-gray-300'}
      `}
      role="listitem"
    >
      <div className="flex items-start gap-3">
        <Checkbox
          checked={isSelected}
          onChange={onSelect}
          ariaLabel={`Select incident ${id}`}
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <Badge variant="neutral" size="sm">
              {authorityLabels[authority]}
            </Badge>
            <Badge variant={statusVariants[status]} size="sm">
              {statusLabels[status]}
            </Badge>
            <Badge variant={severityVariants[severity]} size="sm">
              {severityLabels[severity]}
            </Badge>
          </div>

          <p className="text-sm text-gray-700 mb-2 line-clamp-2">{description}</p>

          <div className="flex items-center justify-between">
            <time className="text-xs text-gray-500">{dateTime}</time>
            <span className="text-xs text-gray-400">#{id}</span>
          </div>
        </div>

        <button
          type="button"
          onClick={onView}
          className="p-2 text-gray-400 hover:text-[#0b5ac1] transition-colors rounded-lg hover:bg-gray-100"
          aria-label={texts.common.viewDetails}
        >
          <IconEye size={20} />
        </button>
      </div>
    </article>
  );
};

export default IncidentListItem;
