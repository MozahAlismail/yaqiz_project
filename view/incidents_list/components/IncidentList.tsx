import React from 'react';
import { Checkbox } from '../../shared/components';
import { SeverityLevel, IncidentStatus, AuthorityType } from '../../shared/types';
import { IncidentListItem } from './IncidentListItem';
import { texts } from '../../i18n/texts';

interface IncidentItem {
  id: string;
  description: string;
  status: IncidentStatus;
  severity: SeverityLevel;
  authority: AuthorityType;
  dateTime: string;
}

interface IncidentListProps {
  incidents: IncidentItem[];
  selectedIds: string[];
  onSelectAll: (selected: boolean) => void;
  onSelectItem: (id: string, selected: boolean) => void;
  onViewItem: (id: string) => void;
}

export const IncidentList: React.FC<IncidentListProps> = ({
  incidents,
  selectedIds,
  onSelectAll,
  onSelectItem,
  onViewItem,
}) => {
  const allSelected = incidents.length > 0 && selectedIds.length === incidents.length;
  const someSelected = selectedIds.length > 0 && selectedIds.length < incidents.length;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded-lg">
        <Checkbox
          checked={allSelected}
          indeterminate={someSelected}
          onChange={onSelectAll}
          label={texts.incidentsList.selectAll}
        />
        <span className="text-sm text-gray-500">
          {incidents.length} {texts.navigation.incidents}
        </span>
      </div>

      <div className="space-y-2" role="list" aria-label={texts.navigation.incidents}>
        {incidents.length > 0 ? (
          incidents.map((incident) => (
            <IncidentListItem
              key={incident.id}
              id={incident.id}
              description={incident.description}
              status={incident.status}
              severity={incident.severity}
              authority={incident.authority}
              dateTime={incident.dateTime}
              isSelected={selectedIds.includes(incident.id)}
              onSelect={(selected) => onSelectItem(incident.id, selected)}
              onView={() => onViewItem(incident.id)}
            />
          ))
        ) : (
          <div className="text-center py-12 text-gray-500">
            {texts.common.noData}
          </div>
        )}
      </div>
    </div>
  );
};

export default IncidentList;
