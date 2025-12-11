import React from 'react';
import { Button, Timer, LiveIndicator } from '../../shared/components';
import { IconMicrophone, IconMicrophoneOff } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface CallHeaderProps {
  callDuration: number;
  isLive: boolean;
  isRecording: boolean;
  onToggleRecording: () => void;
}

export const CallHeader: React.FC<CallHeaderProps> = ({
  callDuration,
  isLive,
  isRecording,
  onToggleRecording,
}) => {
  return (
    <header className="flex items-center justify-between bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
      <div className="flex items-center gap-4">
        <Timer seconds={callDuration} size="lg" />
        <LiveIndicator isLive={isLive} label={texts.common.live} />
      </div>

      <div className="flex items-center gap-3">
        <Button
          variant={isRecording ? 'danger' : 'primary'}
          size="md"
          icon={isRecording ? <IconMicrophoneOff size={18} /> : <IconMicrophone size={18} />}
          onClick={onToggleRecording}
          ariaLabel={isRecording ? texts.realtime.stopRecording : texts.realtime.startRecording}
        >
          {isRecording ? texts.realtime.stopRecording : texts.realtime.startRecording}
        </Button>
      </div>
    </header>
  );
};

export default CallHeader;
