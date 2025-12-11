import React from 'react';
import { QuickFilter } from '../types';

interface FilterChipsProps {
  filters: QuickFilter[];
  selectedId: string;
  onChange: (id: string) => void;
  className?: string;
}

export const FilterChips: React.FC<FilterChipsProps> = ({
  filters,
  selectedId,
  onChange,
  className = '',
}) => {
  return (
    <div className={`flex flex-wrap gap-2 ${className}`} role="group" aria-label="Quick filters">
      {filters.map((filter) => {
        const isSelected = selectedId === filter.id;

        return (
          <button
            key={filter.id}
            type="button"
            onClick={() => onChange(filter.id)}
            aria-pressed={isSelected}
            className={`
              px-4 py-2 rounded-full text-sm font-medium
              transition-colors duration-200
              ${isSelected
                ? 'bg-[#0b5ac1] text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }
            `}
          >
            {filter.label}
          </button>
        );
      })}
    </div>
  );
};

export default FilterChips;
