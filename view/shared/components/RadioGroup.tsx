import React from 'react';
import { SelectOption } from '../types';

interface RadioGroupProps {
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  name: string;
  label?: string;
  disabled?: boolean;
  direction?: 'horizontal' | 'vertical';
  className?: string;
  ariaLabel?: string;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  value,
  onChange,
  options,
  name,
  label,
  disabled = false,
  direction = 'vertical',
  className = '',
  ariaLabel,
}) => {
  return (
    <div className={className} role="radiogroup" aria-label={ariaLabel || label}>
      {label && (
        <p className="text-sm font-medium text-gray-700 mb-2">{label}</p>
      )}
      <div
        className={`
          flex gap-3
          ${direction === 'horizontal' ? 'flex-row flex-wrap' : 'flex-col'}
        `}
      >
        {options.map((option) => (
          <label
            key={option.value}
            className={`
              flex items-center gap-2 cursor-pointer
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={(e) => onChange(e.target.value)}
              disabled={disabled}
              className="sr-only"
            />
            <span
              className={`
                w-5 h-5 rounded-full border-2 flex items-center justify-center
                transition-colors duration-200
                ${value === option.value
                  ? 'border-[#0b5ac1] bg-[#0b5ac1]'
                  : 'border-gray-300 bg-white'
                }
              `}
            >
              {value === option.value && (
                <span className="w-2 h-2 rounded-full bg-white" />
              )}
            </span>
            <span className="text-sm text-gray-700">{option.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default RadioGroup;
