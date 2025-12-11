import React from 'react';
import { Card, HighlightedText, ProgressBar, TextSegment } from '../../shared/components';
import { texts } from '../../i18n/texts';

interface SystemRecommendationPanelProps {
  segments: TextSegment[];
  confidence: number;
  onEditText?: () => void;
}

export const SystemRecommendationPanel: React.FC<SystemRecommendationPanelProps> = ({
  segments,
  confidence,
  onEditText,
}) => {
  return (
    <Card
      title={texts.acceptedIncident.systemRecommendation}
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
    >
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            {texts.acceptedIncident.extractedText}
          </h4>
          <div className="bg-gray-50 rounded-lg p-4">
            <HighlightedText segments={segments} />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {texts.acceptedIncident.confidenceLevel}
            </span>
            <span className="text-lg font-bold text-[#02a63e]">{confidence}%</span>
          </div>
          <ProgressBar
            value={confidence}
            segments={10}
            variant="success"
            size="md"
          />
        </div>
      </div>
    </Card>
  );
};

export default SystemRecommendationPanel;
