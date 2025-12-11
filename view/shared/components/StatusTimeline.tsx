import React from 'react';
import { StatusLogEntry } from '../types';

interface StatusTimelineProps {
  entries: StatusLogEntry[];
  title?: string;
  className?: string;
}

const statusColors = {
  info: 'bg-blue-500',
  success: 'bg-green-500',
  warning: 'bg-yellow-500',
  error: 'bg-red-500',
};

export const StatusTimeline: React.FC<StatusTimelineProps> = ({
  entries,
  title,
  className = '',
}) => {
  return (
    <div className={className}>
      {title && (
        <h4 className="text-sm font-semibold text-gray-900 mb-3">{title}</h4>
      )}
      <div className="relative">
        <div className="absolute top-0 bottom-0 right-2 w-0.5 bg-gray-200" />
        <ul className="space-y-3" role="list">
          {entries.map((entry, index) => (
            <li key={entry.id} className="relative flex items-start gap-3 pr-6">
              <span
                className={`
                  absolute right-0 w-4 h-4 rounded-full border-2 border-white
                  ${statusColors[entry.type]}
                `}
                style={{ top: '2px' }}
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900">{entry.message}</p>
                <time className="text-xs text-gray-500">{entry.timestamp}</time>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default StatusTimeline;
