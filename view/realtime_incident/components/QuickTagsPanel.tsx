import React from 'react';
import { Card, Tag } from '../../shared/components';
import { texts } from '../../i18n/texts';

interface QuickTag {
  id: string;
  label: string;
  variant: 'urgent' | 'accident' | 'injury' | 'fire' | 'custom';
}

interface QuickTagsPanelProps {
  tags: QuickTag[];
  selectedTags: string[];
  onTagToggle: (tagId: string) => void;
}

export const QuickTagsPanel: React.FC<QuickTagsPanelProps> = ({
  tags,
  selectedTags,
  onTagToggle,
}) => {
  return (
    <Card title={texts.realtime.quickTags}>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <Tag
            key={tag.id}
            variant={tag.variant}
            selected={selectedTags.includes(tag.id)}
            onClick={() => onTagToggle(tag.id)}
          >
            {tag.label}
          </Tag>
        ))}
      </div>
    </Card>
  );
};

export default QuickTagsPanel;
