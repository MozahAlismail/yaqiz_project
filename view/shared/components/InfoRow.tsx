import React from 'react';

interface InfoRowProps {
  label: string;
  value: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export const InfoRow: React.FC<InfoRowProps> = ({
  label,
  value,
  icon,
  className = '',
}) => {
  return (
    <div className={`flex items-start gap-3 ${className}`}>
      {icon && <span className="flex-shrink-0 text-gray-400 mt-0.5">{icon}</span>}
      <div className="flex-1 min-w-0">
        <dt className="text-xs text-gray-500">{label}</dt>
        <dd className="text-sm font-medium text-gray-900 mt-0.5">{value}</dd>
      </div>
    </div>
  );
};

export default InfoRow;
