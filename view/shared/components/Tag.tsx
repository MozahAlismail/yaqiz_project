import React from 'react';

export type TagVariant = 'default' | 'urgent' | 'accident' | 'injury' | 'fire' | 'custom';

interface TagProps {
  children: React.ReactNode;
  variant?: TagVariant;
  selected?: boolean;
  onClick?: () => void;
  removable?: boolean;
  onRemove?: () => void;
  className?: string;
  ariaLabel?: string;
  customColor?: string;
}

const variantStyles: Record<TagVariant, { bg: string; text: string; selectedBg: string }> = {
  default: { bg: 'bg-gray-100', text: 'text-gray-700', selectedBg: 'bg-gray-300' },
  urgent: { bg: 'bg-red-50', text: 'text-red-700', selectedBg: 'bg-red-200' },
  accident: { bg: 'bg-orange-50', text: 'text-orange-700', selectedBg: 'bg-orange-200' },
  injury: { bg: 'bg-yellow-50', text: 'text-yellow-700', selectedBg: 'bg-yellow-200' },
  fire: { bg: 'bg-red-50', text: 'text-red-700', selectedBg: 'bg-red-200' },
  custom: { bg: 'bg-blue-50', text: 'text-blue-700', selectedBg: 'bg-blue-200' },
};

export const Tag: React.FC<TagProps> = ({
  children,
  variant = 'default',
  selected = false,
  onClick,
  removable = false,
  onRemove,
  className = '',
  ariaLabel,
  customColor,
}) => {
  const styles = variantStyles[variant];
  const bgColor = customColor ? customColor : selected ? styles.selectedBg : styles.bg;

  return (
    <span
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={ariaLabel}
      aria-pressed={onClick ? selected : undefined}
      onClick={onClick}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
      className={`
        inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium
        transition-colors duration-200
        ${bgColor} ${styles.text}
        ${onClick ? 'cursor-pointer hover:opacity-80' : ''}
        ${className}
      `}
      style={customColor ? { backgroundColor: customColor } : undefined}
    >
      <span>{children}</span>
      {removable && onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="flex-shrink-0 hover:opacity-70 focus:outline-none"
          aria-label="Remove tag"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10.5 3.5L3.5 10.5M3.5 3.5L10.5 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      )}
    </span>
  );
};

export default Tag;
