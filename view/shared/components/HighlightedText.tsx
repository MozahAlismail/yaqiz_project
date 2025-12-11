import React from 'react';

export interface TextSegment {
  text: string;
  type: 'normal' | 'keyword' | 'location' | 'name' | 'highlight';
}

interface HighlightedTextProps {
  segments: TextSegment[];
  className?: string;
}

const segmentColors = {
  normal: 'text-gray-700',
  keyword: 'bg-red-100 text-red-800 px-1 rounded',
  location: 'bg-blue-100 text-blue-800 px-1 rounded',
  name: 'bg-green-100 text-green-800 px-1 rounded',
  highlight: 'bg-yellow-100 text-yellow-800 px-1 rounded',
};

export const HighlightedText: React.FC<HighlightedTextProps> = ({
  segments,
  className = '',
}) => {
  return (
    <p className={`text-sm leading-relaxed [direction:rtl] ${className}`}>
      {segments.map((segment, index) => (
        <span key={index} className={segmentColors[segment.type]}>
          {segment.text}
        </span>
      ))}
    </p>
  );
};

export default HighlightedText;
