import React from 'react';
import { Card, Button, TextArea } from '../../shared/components';
import { Note } from '../../shared/types';
import { IconPlus } from '../../shared/icons';
import { texts } from '../../i18n/texts';

interface OperatorNotesPanelProps {
  notes: Note[];
  isAddingNote: boolean;
  newNoteContent: string;
  onNewNoteChange: (value: string) => void;
  onAddNoteClick: () => void;
  onSaveNote: () => void;
  onCancelNote: () => void;
}

export const OperatorNotesPanel: React.FC<OperatorNotesPanelProps> = ({
  notes,
  isAddingNote,
  newNoteContent,
  onNewNoteChange,
  onAddNoteClick,
  onSaveNote,
  onCancelNote,
}) => {
  return (
    <Card
      title={texts.acceptedIncident.operatorNotes}
      headerAction={
        !isAddingNote && (
          <Button
            variant="ghost"
            size="sm"
            icon={<IconPlus size={16} />}
            onClick={onAddNoteClick}
          >
            {texts.actions.addNote}
          </Button>
        )
      }
    >
      <div className="space-y-3">
        {notes.length > 0 ? (
          <ul className="space-y-2">
            {notes.map((note) => (
              <li
                key={note.id}
                className="bg-gray-50 rounded-lg p-3 text-sm text-gray-700"
              >
                <p>{note.content}</p>
                <time className="text-xs text-gray-400 mt-1 block">
                  {note.createdAt}
                </time>
              </li>
            ))}
          </ul>
        ) : (
          !isAddingNote && (
            <p className="text-sm text-gray-500 text-center py-4">
              {texts.common.noData}
            </p>
          )
        )}

        {isAddingNote && (
          <div className="space-y-3">
            <TextArea
              value={newNoteContent}
              onChange={onNewNoteChange}
              placeholder={texts.placeholders.enterNotes}
              rows={3}
            />
            <div className="flex gap-2 justify-end">
              <Button variant="ghost" size="sm" onClick={onCancelNote}>
                {texts.common.cancel}
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={onSaveNote}
                disabled={!newNoteContent.trim()}
              >
                {texts.actions.saveNote}
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default OperatorNotesPanel;
