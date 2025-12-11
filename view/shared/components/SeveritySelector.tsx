import React from 'react';
import { SeverityLevel } from '../types';

interface SeveritySelectorProps {
  value: SeverityLevel | '';
  onChange: (value: SeverityLevel) => void;
  options: { value: SeverityLevel; label: string }[];
  label?: string;
  disabled?: boolean;
  className?: string;
}

const severityColors: Record<SeverityLevel, { bg: string; activeBg: string; text: string }> = {
  critical: { bg: 'bg-gray-100', activeBg: 'bg-red-600', text: 'text-white' },
  high: { bg: 'bg-gray-100', activeBg: 'bg-red-500', text: 'text-white' },
  medium: { bg: 'bg-gray-100', activeBg: 'bg-yellow-500', text: 'text-white' },
  low: { bg: 'bg-gray-100', activeBg: 'bg-green-500', text: 'text-white' },
};

export const SeveritySelector: React.FC<SeveritySelectorProps> = ({
  value,
  onChange,
  options,
  label,
  disabled = false,
  className = '',
}) => {
  return (
    <div className={className}>
      {label && (
        <p className="text-sm font-medium text-gray-700 mb-2">{label}</p>
      )}
      <div className="flex gap-2" role="group" aria-label={label}>
        {options.map((option) => {
          const isSelected = value === option.value;
          const colors = severityColors[option.value];

          return (
            <button
              key={option.value}
              type="button"
              onClick={() => onChange(option.value)}
              disabled={disabled}
              aria-pressed={isSelected}
              className={`
                flex-1 px-4 py-2 rounded-lg text-sm font-medium
                transition-colors duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
                ${isSelected ? `${colors.activeBg} ${colors.text}` : `${colors.bg} text-gray-700 hover:bg-gray-200`}
              `}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default SeveritySelector;
