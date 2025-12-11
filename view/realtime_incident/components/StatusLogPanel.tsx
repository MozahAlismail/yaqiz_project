import React from 'react';
import { Card, StatusTimeline } from '../../shared/components';
import { StatusLogEntry } from '../../shared/types';
import { texts } from '../../i18n/texts';

interface StatusLogPanelProps {
  entries: StatusLogEntry[];
}

export const StatusLogPanel: React.FC<StatusLogPanelProps> = ({
  entries,
}) => {
  return (
    <Card title={texts.realtime.statusLog}>
      <StatusTimeline entries={entries} />
    </Card>
  );
};

export default StatusLogPanel;
