import React from 'react';

interface TimerProps {
  seconds: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeStyles = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-xl',
};

export const Timer: React.FC<TimerProps> = ({
  seconds,
  className = '',
  size = 'md',
}) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const formatNumber = (n: number) => n.toString().padStart(2, '0');

  const display = hours > 0
    ? `${formatNumber(hours)}:${formatNumber(minutes)}:${formatNumber(secs)}`
    : `${formatNumber(minutes)}:${formatNumber(secs)}`;

  return (
    <time
      className={`font-mono font-semibold text-gray-900 ${sizeStyles[size]} ${className}`}
      aria-label={`Duration: ${display}`}
    >
      {display}
    </time>
  );
};

export default Timer;
