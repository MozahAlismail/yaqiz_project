import React from 'react';

interface LiveIndicatorProps {
  isLive: boolean;
  label?: string;
  showPulse?: boolean;
  className?: string;
}

export const LiveIndicator: React.FC<LiveIndicatorProps> = ({
  isLive,
  label,
  showPulse = true,
  className = '',
}) => {
  if (!isLive) return null;

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <span className="relative flex h-3 w-3">
        {showPulse && (
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
        )}
        <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500" />
      </span>
      {label && (
        <span className="text-sm font-medium text-red-600">{label}</span>
      )}
    </div>
  );
};

export default LiveIndicator;
