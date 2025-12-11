import React from 'react';
import { Card, HighlightedText, TextSegment } from '../../shared/components';
import { texts } from '../../i18n/texts';

interface TranscriptionPanelProps {
  segments: TextSegment[];
  onEditText?: () => void;
}

export const TranscriptionPanel: React.FC<TranscriptionPanelProps> = ({
  segments,
  onEditText,
}) => {
  return (
    <Card
      title={texts.realtime.convertedText}
      headerAction={
        onEditText && (
          <button
            type="button"
            onClick={onEditText}
            className="text-sm text-[#0b5ac1] hover:underline"
          >
            {texts.acceptedIncident.editText}
          </button>
        )
      }
      className="h-full"
    >
      <div className="bg-gray-50 rounded-lg p-4 min-h-[200px]">
        <HighlightedText segments={segments} />
      </div>
    </Card>
  );
};

export default TranscriptionPanel;
