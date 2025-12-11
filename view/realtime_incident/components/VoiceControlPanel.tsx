import React from 'react';
import { Card, Slider, Toggle } from '../../shared/components';
import { IconVolume } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface VoiceControlPanelProps {
  volume: number;
  isTranslationEnabled: boolean;
  onVolumeChange: (value: number) => void;
  onTranslationToggle: (enabled: boolean) => void;
}

export const VoiceControlPanel: React.FC<VoiceControlPanelProps> = ({
  volume,
  isTranslationEnabled,
  onVolumeChange,
  onTranslationToggle,
}) => {
  return (
    <Card title={texts.realtime.voiceControl}>
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <IconVolume size={20} className="text-gray-500" />
          <Slider
            value={volume}
            onChange={onVolumeChange}
            min={0}
            max={100}
            className="flex-1"
            ariaLabel={texts.realtime.voiceControl}
          />
        </div>

        <Toggle
          checked={isTranslationEnabled}
          onChange={onTranslationToggle}
          label={texts.realtime.translation}
        />
      </div>
    </Card>
  );
};

export default VoiceControlPanel;
