import React from 'react';
import { Button, Timer, LiveIndicator } from '../../shared/components';
import { IconSave, IconPhoneOff } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface CallHeaderProps {
  callDuration: number;
  isLive: boolean;
  onSave: () => void;
  onEndCall: () => void;
  isSaving?: boolean;
}

export const CallHeader: React.FC<CallHeaderProps> = ({
  callDuration,
  isLive,
  onSave,
  onEndCall,
  isSaving = false,
}) => {
  return (
    <header className="flex items-center justify-between bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
      <div className="flex items-center gap-4">
        <Timer seconds={callDuration} size="lg" />
        <LiveIndicator isLive={isLive} label={texts.common.live} />
      </div>

      <div className="flex items-center gap-3">
        {isSaving && (
          <span className="text-sm text-gray-500">{texts.common.autoSaving}</span>
        )}
        <Button
          variant="success"
          size="md"
          icon={<IconSave size={18} />}
          onClick={onSave}
          ariaLabel={texts.common.save}
        >
          {texts.common.save}
        </Button>
        <Button
          variant="warning"
          size="md"
          icon={<IconPhoneOff size={18} />}
          onClick={onEndCall}
          ariaLabel={texts.actions.endCall}
        >
          {texts.actions.endCall}
        </Button>
      </div>
    </header>
  );
};

export default CallHeader;
