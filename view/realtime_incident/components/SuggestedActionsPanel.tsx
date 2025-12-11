import React from 'react';
import { Card, ActionList, ActionItem } from '../../shared/components';
import { IconCheck, IconTransfer, IconInfo } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface SuggestedActionsPanelProps {
  onAction: (actionId: string) => void;
}

const defaultActions: ActionItem[] = [
  {
    id: 'confirm',
    label: texts.actions.confirmReport,
    icon: <IconCheck size={18} />,
    variant: 'success',
  },
  {
    id: 'transfer',
    label: texts.actions.transferToAuthority,
    icon: <IconTransfer size={18} />,
    variant: 'primary',
  },
  {
    id: 'request_info',
    label: texts.actions.requestMoreInfo,
    icon: <IconInfo size={18} />,
    variant: 'warning',
  },
];

export const SuggestedActionsPanel: React.FC<SuggestedActionsPanelProps> = ({
  onAction,
}) => {
  return (
    <Card title={texts.realtime.suggestedActions}>
      <ActionList items={defaultActions} onAction={onAction} />
    </Card>
  );
};

export default SuggestedActionsPanel;
