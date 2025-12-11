import React from 'react';

interface ListItemProps {
  children: React.ReactNode;
  selected?: boolean;
  onClick?: () => void;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
  ariaLabel?: string;
}

export const ListItem: React.FC<ListItemProps> = ({
  children,
  selected = false,
  onClick,
  icon,
  action,
  className = '',
  ariaLabel,
}) => {
  return (
    <div
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      aria-label={ariaLabel}
      aria-selected={selected}
      onClick={onClick}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick();
        }
      }}
      className={`
        flex items-center gap-3 p-3 rounded-lg transition-colors duration-200
        ${selected ? 'bg-blue-50 border border-blue-200' : 'bg-white border border-transparent'}
        ${onClick ? 'cursor-pointer hover:bg-gray-50' : ''}
        ${className}
      `}
    >
      {icon && <span className="flex-shrink-0 text-gray-400">{icon}</span>}
      <div className="flex-1 min-w-0">{children}</div>
      {action && <span className="flex-shrink-0">{action}</span>}
    </div>
  );
};

export default ListItem;
