import React from 'react';

interface ProgressBarProps {
  value: number;
  max?: number;
  showLabel?: boolean;
  label?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  segments?: number;
  className?: string;
  ariaLabel?: string;
}

const variantStyles = {
  default: 'bg-[#0b5ac1]',
  success: 'bg-[#02a63e]',
  warning: 'bg-[#f1b100]',
  danger: 'bg-[#bf0f0c]',
};

const sizeStyles = {
  sm: 'h-1',
  md: 'h-2',
  lg: 'h-3',
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  showLabel = false,
  label,
  variant = 'default',
  size = 'md',
  segments,
  className = '',
  ariaLabel,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  if (segments) {
    const segmentWidth = 100 / segments;
    const filledSegments = Math.floor((percentage / 100) * segments);

    return (
      <div className={className}>
        {(label || showLabel) && (
          <div className="flex justify-between mb-1">
            {label && <span className="text-sm text-gray-600">{label}</span>}
            {showLabel && <span className="text-sm font-medium text-gray-900">{Math.round(percentage)}%</span>}
          </div>
        )}
        <div
          className={`flex gap-1 ${sizeStyles[size]}`}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
          aria-label={ariaLabel || label}
        >
          {Array.from({ length: segments }).map((_, index) => (
            <div
              key={index}
              className={`
                flex-1 rounded-sm transition-colors duration-300
                ${index < filledSegments ? variantStyles[variant] : 'bg-gray-200'}
              `}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      {(label || showLabel) && (
        <div className="flex justify-between mb-1">
          {label && <span className="text-sm text-gray-600">{label}</span>}
          {showLabel && <span className="text-sm font-medium text-gray-900">{Math.round(percentage)}%</span>}
        </div>
      )}
      <div
        className={`w-full bg-gray-200 rounded-full overflow-hidden ${sizeStyles[size]}`}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={ariaLabel || label}
      >
        <div
          className={`${variantStyles[variant]} rounded-full transition-all duration-300 h-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
