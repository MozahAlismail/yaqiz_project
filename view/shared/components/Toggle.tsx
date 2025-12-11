import React from 'react';

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  id?: string;
  ariaLabel?: string;
}

const sizeStyles = {
  sm: {
    track: 'w-8 h-4',
    thumb: 'w-3 h-3',
    translate: 'translate-x-4',
  },
  md: {
    track: 'w-11 h-6',
    thumb: 'w-5 h-5',
    translate: 'translate-x-5',
  },
  lg: {
    track: 'w-14 h-7',
    thumb: 'w-6 h-6',
    translate: 'translate-x-7',
  },
};

export const Toggle: React.FC<ToggleProps> = ({
  checked,
  onChange,
  label,
  disabled = false,
  size = 'md',
  className = '',
  id,
  ariaLabel,
}) => {
  const inputId = id || `toggle-${Math.random().toString(36).substr(2, 9)}`;
  const styles = sizeStyles[size];

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <button
        id={inputId}
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={ariaLabel || label}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={`
          relative inline-flex flex-shrink-0 rounded-full
          transition-colors duration-200 ease-in-out
          focus:outline-none focus:ring-2 focus:ring-[#0b5ac1] focus:ring-offset-2
          disabled:opacity-50 disabled:cursor-not-allowed
          ${styles.track}
          ${checked ? 'bg-[#02a63e]' : 'bg-gray-300'}
        `}
      >
        <span
          className={`
            pointer-events-none inline-block rounded-full bg-white shadow-lg
            transform transition-transform duration-200 ease-in-out
            ${styles.thumb}
            ${checked ? styles.translate : 'translate-x-0'}
          `}
          style={{ marginTop: '0.125rem', marginRight: '0.125rem' }}
        />
      </button>
      {label && (
        <label
          htmlFor={inputId}
          className="text-sm font-medium text-gray-700 cursor-pointer"
        >
          {label}
        </label>
      )}
    </div>
  );
};

export default Toggle;
