import React from 'react';
import { Button } from '../../shared/components';
import { texts } from '../../i18n/texts';

interface CallFooterProps {
  onConfirm: () => void;
  isAutoSaving?: boolean;
}

export const CallFooter: React.FC<CallFooterProps> = ({
  onConfirm,
  isAutoSaving = false,
}) => {
  return (
    <footer className="flex items-center justify-between bg-white border-t border-gray-200 px-4 py-3 sm:px-6">
      <div>
        {isAutoSaving && (
          <span className="text-sm text-gray-500 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            {texts.common.autoSaving}
          </span>
        )}
      </div>

      <Button variant="success" size="md" onClick={onConfirm}>
        {texts.common.confirm}
      </Button>
    </footer>
  );
};

export default CallFooter;
