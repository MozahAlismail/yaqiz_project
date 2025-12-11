import React from 'react';
import { Card, TextArea } from '../../shared/components';
import { texts } from '../../i18n/texts';

interface QuickNotesPanelProps {
  notes: string;
  onNotesChange: (value: string) => void;
}

export const QuickNotesPanel: React.FC<QuickNotesPanelProps> = ({
  notes,
  onNotesChange,
}) => {
  return (
    <Card title={texts.realtime.quickNotes}>
      <TextArea
        value={notes}
        onChange={onNotesChange}
        placeholder={texts.placeholders.enterNotes}
        rows={4}
        resize="none"
      />
    </Card>
  );
};

export default QuickNotesPanel;
