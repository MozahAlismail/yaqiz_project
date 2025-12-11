import React from 'react';
import { Card, FeedbackButtons } from '../../shared/components';
import { texts } from '../../i18n/texts';

interface FeedbackPanelProps {
  value: 'yes' | 'no' | null;
  onChange: (value: 'yes' | 'no') => void;
}

export const FeedbackPanel: React.FC<FeedbackPanelProps> = ({
  value,
  onChange,
}) => {
  return (
    <Card title={texts.acceptedIncident.analysisAccuracy}>
      <FeedbackButtons
        value={value}
        onChange={onChange}
        question={texts.acceptedIncident.feedbackQuestion}
        yesLabel={texts.common.yes}
        noLabel={texts.common.no}
      />
    </Card>
  );
};

export default FeedbackPanel;
