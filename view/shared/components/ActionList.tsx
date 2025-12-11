import React from 'react';

export interface ActionItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
}

interface ActionListProps {
  items: ActionItem[];
  onAction: (id: string) => void;
  title?: string;
  className?: string;
}

const variantStyles = {
  default: 'text-gray-700 hover:bg-gray-100',
  primary: 'text-blue-700 hover:bg-blue-50',
  success: 'text-green-700 hover:bg-green-50',
  warning: 'text-orange-700 hover:bg-orange-50',
  danger: 'text-red-700 hover:bg-red-50',
};

export const ActionList: React.FC<ActionListProps> = ({
  items,
  onAction,
  title,
  className = '',
}) => {
  return (
    <div className={className}>
      {title && (
        <h4 className="text-sm font-semibold text-gray-900 mb-3">{title}</h4>
      )}
      <ul className="space-y-1" role="list">
        {items.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              onClick={() => onAction(item.id)}
              className={`
                w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                text-sm font-medium transition-colors duration-200
                ${variantStyles[item.variant || 'default']}
              `}
            >
              {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
              <span>{item.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ActionList;
