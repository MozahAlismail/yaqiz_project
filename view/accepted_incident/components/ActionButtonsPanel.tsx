import React from 'react';
import { Button } from '../../shared/components';
import { IconTransfer, IconX } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface ActionButtonsPanelProps {
  onTransfer: () => void;
  onClose: () => void;
}

export const ActionButtonsPanel: React.FC<ActionButtonsPanelProps> = ({
  onTransfer,
  onClose,
}) => {
  return (
    <div className="flex items-center justify-end gap-3 bg-white border-t border-gray-200 px-4 py-3 sm:px-6">
      <Button
        variant="success"
        size="md"
        icon={<IconTransfer size={18} />}
        onClick={onTransfer}
      >
        {texts.actions.transfer}
      </Button>
      <Button
        variant="danger"
        size="md"
        icon={<IconX size={18} />}
        onClick={onClose}
      >
        {texts.actions.closeReport}
      </Button>
    </div>
  );
};

export default ActionButtonsPanel;
