import React from 'react';

interface TextAreaProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  error?: string;
  label?: string;
  rows?: number;
  maxLength?: number;
  fullWidth?: boolean;
  className?: string;
  id?: string;
  name?: string;
  required?: boolean;
  ariaLabel?: string;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
}

export const TextArea: React.FC<TextAreaProps> = ({
  value,
  onChange,
  placeholder,
  disabled = false,
  error,
  label,
  rows = 4,
  maxLength,
  fullWidth = true,
  className = '',
  id,
  name,
  required = false,
  ariaLabel,
  resize = 'vertical',
}) => {
  const inputId = id || name || `textarea-${Math.random().toString(36).substr(2, 9)}`;

  const resizeClass = {
    none: 'resize-none',
    vertical: 'resize-y',
    horizontal: 'resize-x',
    both: 'resize',
  };

  return (
    <div className={`${fullWidth ? 'w-full' : ''} ${className}`}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
          {required && <span className="text-red-500 mr-1">*</span>}
        </label>
      )}
      <textarea
        id={inputId}
        name={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        rows={rows}
        maxLength={maxLength}
        aria-label={ariaLabel || label}
        aria-invalid={!!error}
        aria-describedby={error ? `${inputId}-error` : undefined}
        className={`
          w-full px-4 py-2.5 rounded-lg border transition-colors duration-200
          bg-white text-gray-900 placeholder-gray-400
          focus:outline-none focus:ring-2 focus:ring-[#0b5ac1] focus:border-transparent
          disabled:bg-gray-100 disabled:cursor-not-allowed
          ${resizeClass[resize]}
          ${error ? 'border-red-500' : 'border-gray-300'}
          [direction:rtl]
        `}
      />
      <div className="flex justify-between mt-1">
        {error && (
          <p id={`${inputId}-error`} className="text-sm text-red-500">
            {error}
          </p>
        )}
        {maxLength && (
          <span className="text-sm text-gray-400 mr-auto">
            {value.length}/{maxLength}
          </span>
        )}
      </div>
    </div>
  );
};

export default TextArea;
