import React from 'react';

interface FeedbackButtonsProps {
  value: 'yes' | 'no' | null;
  onChange: (value: 'yes' | 'no') => void;
  question?: string;
  yesLabel: string;
  noLabel: string;
  disabled?: boolean;
  className?: string;
}

export const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({
  value,
  onChange,
  question,
  yesLabel,
  noLabel,
  disabled = false,
  className = '',
}) => {
  return (
    <div className={className}>
      {question && (
        <p className="text-sm font-medium text-gray-700 mb-3">{question}</p>
      )}
      <div className="flex gap-3" role="group" aria-label={question}>
        <button
          type="button"
          onClick={() => onChange('yes')}
          disabled={disabled}
          aria-pressed={value === 'yes'}
          className={`
            flex-1 px-4 py-2.5 rounded-lg text-sm font-medium
            transition-colors duration-200
            disabled:opacity-50 disabled:cursor-not-allowed
            ${value === 'yes'
              ? 'bg-green-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }
          `}
        >
          {yesLabel}
        </button>
        <button
          type="button"
          onClick={() => onChange('no')}
          disabled={disabled}
          aria-pressed={value === 'no'}
          className={`
            flex-1 px-4 py-2.5 rounded-lg text-sm font-medium
            transition-colors duration-200
            disabled:opacity-50 disabled:cursor-not-allowed
            ${value === 'no'
              ? 'bg-red-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }
          `}
        >
          {noLabel}
        </button>
      </div>
    </div>
  );
};

export default FeedbackButtons;
